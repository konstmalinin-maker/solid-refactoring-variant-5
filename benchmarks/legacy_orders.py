"""Literal 1000-order task: auxiliary legacy prototype, not variant 5 source."""
from decimal import ROUND_HALF_UP, Decimal

from solid.infrastructure.order_repository import MemoryOrderRepository


class LegacyOrderProcessor:
    def __init__(self):
        self.repository = MemoryOrderRepository()

    def process_order(self, order):
        total = sum((line.price * line.quantity for line in order.items), Decimal(0))
        if order.user_type == "regular":
            rate = Decimal("0.05")
        elif order.user_type == "vip":
            rate = Decimal("0.10")
        elif order.user_type == "premium":
            rate = Decimal("0.15")
        elif order.user_type == "student":
            rate = Decimal("0.20")
        else:
            rate = Decimal(0)
        total = (total * (1 - rate)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return self.repository.save(order, total)
