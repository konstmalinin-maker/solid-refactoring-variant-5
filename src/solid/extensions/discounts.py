"""A: discount Strategy products for the exact order example in the PDF."""
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from typing import Protocol


class DiscountPolicy(Protocol):
    def apply(self, total: Decimal) -> Decimal: ...


@dataclass(frozen=True)
class PercentageDiscount:
    rate: Decimal

    def __post_init__(self):
        if not Decimal(0) <= self.rate <= Decimal(1):
            raise ValueError("rate must be between 0 and 1")

    def apply(self, total):
        return (total * (1 - self.rate)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class NoDiscount:
    def apply(self, total):
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
