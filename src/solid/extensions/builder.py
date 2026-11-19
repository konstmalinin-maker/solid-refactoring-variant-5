"""B: object construction is separate from pricing, persistence and delivery."""
from decimal import Decimal

from solid.extensions.order import Order, OrderLine


class OrderBuilder:
    def __init__(self):
        self.values, self.items = {}, []

    def for_user(self, user_id, email, user_type="regular"):
        self.values.update(user_id=user_id, email=email, user_type=user_type)
        return self

    def add_item(self, name, price, quantity=1):
        self.items.append(OrderLine(name.strip(), Decimal(str(price)), quantity))
        return self

    def with_notes(self, notes):
        self.values["notes"] = notes
        return self

    def deliver_to(self, address):
        self.values["delivery_address"] = address
        return self

    def in_currency(self, currency):
        self.values["currency"] = currency
        return self

    def build(self):
        if "user_id" not in self.values:
            raise ValueError("user is required")
        return Order(items=tuple(self.items), **self.values)
