"""Order processing uses the Factory Method and injected repository."""
from decimal import Decimal
from typing import Protocol

from solid.extensions.factory import DiscountFactory


class OrderRepository(Protocol):
    def save(self, order, total): ...


class OrderService:
    def __init__(self, repository: OrderRepository, factory: DiscountFactory):
        self.repository, self.factory = repository, factory

    def process_order(self, order):
        total = sum((line.price * line.quantity for line in order.items), Decimal(0))
        policy = self.factory.create(order.user_type)
        return self.repository.save(order, policy.apply(total))
