"""Immutable complex Order and its validated lines."""
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class OrderLine:
    name: str
    price: Decimal
    quantity: int

    def __post_init__(self):
        if not self.name.strip() or self.price < 0 or type(self.quantity) is not int or self.quantity <= 0:
            raise ValueError("invalid item")


@dataclass(frozen=True)
class Order:
    user_id: int
    email: str
    items: tuple[OrderLine, ...]
    user_type: str = "regular"
    currency: str = "RUB"
    notes: str = ""
    delivery_address: str | None = None

    def __post_init__(self):
        if type(self.user_id) is not int or self.user_id <= 0:
            raise ValueError("invalid user_id")
        if "@" not in self.email or not self.email.strip():
            raise ValueError("invalid email")
        if not self.items:
            raise ValueError("items are required")
        if self.currency not in ("RUB", "USD", "EUR"):
            raise ValueError("unsupported currency")
