"""Small in-memory order adapter for the additional A-C examples."""
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Receipt:
    id: int
    user_id: int
    total: Decimal
    currency: str


class MemoryOrderRepository:
    def __init__(self):
        self.receipts = []

    def save(self, order, total):
        receipt = Receipt(len(self.receipts) + 1, order.user_id, total, order.currency)
        self.receipts.append(receipt)
        return receipt
