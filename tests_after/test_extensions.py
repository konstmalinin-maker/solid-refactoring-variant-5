from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from main import build_container
from src.extensions.builder import OrderBuilder
from src.extensions.discounts import NoDiscount, PercentageDiscount
from src.extensions.factory import DiscountFactory, RegisteredDiscountFactory
from src.extensions.order import Order, OrderLine
from src.extensions.order_service import OrderRepository, OrderService
from src.infrastructure.container import Container
from src.infrastructure.order_repository import MemoryOrderRepository, Receipt


@pytest.mark.parametrize("kind,expected", [("regular", "95.00"), ("vip", "90.00"),
    ("premium", "85.00"), ("student", "80.00"), ("unknown", "100.00")])
def test_factory_products(kind, expected):
    factory = RegisteredDiscountFactory()
    assert factory.create(kind).apply(Decimal(100)) == Decimal(expected)
    assert factory.create(kind) is not factory.create(kind)


def test_registration_decorator_returns_provider_and_is_isolated():
    factory = RegisteredDiscountFactory()
    def creator():
        return PercentageDiscount(Decimal("0.30"))
    assert factory.register("teacher")(creator) is creator
    assert factory.create("teacher").apply(Decimal(100)) == Decimal("70.00")
    assert RegisteredDiscountFactory().create("teacher").apply(Decimal(100)) == Decimal("100.00")


@pytest.mark.parametrize("rate", [Decimal("-0.01"), Decimal("1.01")])
def test_discount_rate_bounds(rate):
    with pytest.raises(ValueError, match="rate must be between 0 and 1"):
        PercentageDiscount(rate)


@pytest.mark.parametrize("rate,result", [("0", "1.01"), ("1", "0.00"), ("0.1", "0.90")])
def test_discount_boundaries_and_rounding(rate, result):
    assert PercentageDiscount(Decimal(rate)).apply(Decimal("1.005")) == Decimal(result)
    assert NoDiscount().apply(Decimal("1.005")) == Decimal("1.01")


def test_builder_defaults_full_object_immutability_and_snapshots():
    builder = OrderBuilder().for_user(7, "u@example.com")
    assert builder.add_item(" Book ", "125.50", 2) is builder
    first = builder.build()
    assert first == Order(7, "u@example.com", (OrderLine("Book", Decimal("125.50"), 2),))
    assert builder.with_notes("fragile") is builder
    assert builder.deliver_to("Moscow") is builder
    assert builder.in_currency("USD") is builder
    builder.add_item("Pen", 10)
    second = builder.build()
    assert second == Order(7, "u@example.com", first.items + (OrderLine("Pen", Decimal(10), 1),),
                           "regular", "USD", "fragile", "Moscow")
    assert first.notes == "" and first.currency == "RUB" and first.delivery_address is None
    assert len(first.items) == 1
    with pytest.raises(FrozenInstanceError):
        first.user_id = 99


def test_builder_requires_user_and_items():
    with pytest.raises(ValueError, match="user is required"):
        OrderBuilder().build()
    with pytest.raises(ValueError, match="items are required"):
        OrderBuilder().for_user(1, "u@example.com").build()


@pytest.mark.parametrize("uid", [0, -1, True, "1"])
def test_invalid_order_user(uid):
    with pytest.raises(ValueError, match="invalid user_id"):
        OrderBuilder().for_user(uid, "u@example.com").add_item("a", 1).build()


@pytest.mark.parametrize("email", ["", " ", "invalid"])
def test_invalid_email(email):
    with pytest.raises(ValueError, match="invalid email"):
        OrderBuilder().for_user(1, email).add_item("a", 1).build()


@pytest.mark.parametrize("name,price,quantity", [(" ", 1, 1), ("a", -1, 1),
    ("a", 1, 0), ("a", 1, -1), ("a", 1, True), ("a", 1, 1.5)])
def test_invalid_builder_item(name, price, quantity):
    with pytest.raises(ValueError, match="invalid item"):
        OrderBuilder().add_item(name, price, quantity)


def test_currency_and_zero_price():
    for currency in ("RUB", "USD", "EUR"):
        order = OrderBuilder().for_user(1, "a@b").add_item("free", 0).in_currency(currency).build()
        assert order.currency == currency
    with pytest.raises(ValueError, match="unsupported currency"):
        OrderBuilder().for_user(1, "a@b").add_item("a", 1).in_currency("GBP").build()


def test_service_calculates_all_lines_and_persists_receipts():
    repo = MemoryOrderRepository()
    service = OrderService(repo, RegisteredDiscountFactory())
    order = (OrderBuilder().for_user(5, "u@example.com", "student").add_item("a", 100, 2)
             .add_item("b", 50).in_currency("EUR").build())
    assert service.process_order(order) == Receipt(1, 5, Decimal("200.00"), "EUR")
    assert service.process_order(order) == Receipt(2, 5, Decimal("200.00"), "EUR")
    assert repo.receipts == [Receipt(1, 5, Decimal("200.00"), "EUR"), Receipt(2, 5, Decimal("200.00"), "EUR")]


def test_factory_method_can_be_overridden_without_service_edit():
    class FreeFactory(DiscountFactory):
        def create(self, user_type):
            assert user_type == "regular"
            return PercentageDiscount(Decimal(1))
    order = OrderBuilder().for_user(1, "a@b").add_item("a", 100).build()
    assert OrderService(MemoryOrderRepository(), FreeFactory()).process_order(order).total == Decimal("0.00")


def test_container_transients_and_nested_exception_overrides():
    container = Container()
    container.register("object", object)
    assert container.resolve("object") is not container.resolve("object")
    with pytest.raises(KeyError) as exc:
        container.resolve("unknown")
    assert exc.value.args == ("unknown",)
    with container.override("object", lambda: 1) as active:
        assert active is container and container.resolve("object") == 1
        with pytest.raises(RuntimeError):
            with container.override("object", lambda: 2):
                assert container.resolve("object") == 2
                raise RuntimeError("rollback override")
        assert container.resolve("object") == 1
    assert type(container.resolve("object")) is object


def test_main_uses_container_to_replace_order_repository(tmp_path):
    container = build_container(tmp_path)
    class Fake:
        def __init__(self):
            self.calls = []
        def save(self, order, total):
            self.calls.append((order, total))
            return "fake receipt"
    fake = Fake()
    original = container.resolve(OrderRepository)
    assert original is container.resolve(OrderRepository)
    order = OrderBuilder().for_user(1, "a@b", "vip").add_item("a", 100).build()
    with container.override(OrderRepository, lambda: fake):
        assert container.resolve(OrderService).process_order(order) == "fake receipt"
    assert fake.calls == [(order, Decimal("90.00"))]
    assert container.resolve(OrderRepository) is original
    assert isinstance(container.resolve(DiscountFactory), RegisteredDiscountFactory)
