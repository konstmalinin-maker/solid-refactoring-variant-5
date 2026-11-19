"""Intentionally weak assertions: complete line execution does not verify money."""
from decimal import Decimal

import pytest

from solid.extensions.discounts import NoDiscount, PercentageDiscount


def test_smoke_coverage_only():
    for rate in ("0", "0.1", "1"):
        PercentageDiscount(Decimal(rate)).apply(Decimal("1.005"))
    NoDiscount().apply(Decimal("1.005"))
    for rate in ("-0.01", "1.01"):
        with pytest.raises(ValueError):
            PercentageDiscount(Decimal(rate))
