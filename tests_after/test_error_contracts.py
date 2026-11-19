"""Mutation review found substring-only exception assertions; verify exact contracts."""
from decimal import Decimal

import pytest

from solid.compat import DocumentManager
from solid.extensions.builder import OrderBuilder
from solid.extensions.discounts import PercentageDiscount


def test_exact_missing_document_and_version_messages(tmp_path):
    manager = DocumentManager(tmp_path)
    for action in (lambda: manager.export(999, "txt"), lambda: manager.restore(999, 1)):
        with pytest.raises(KeyError) as exc:
            action()
        assert exc.value.args == ("document not found",)
    manager.create("one", "body")
    with pytest.raises(ValueError) as exc:
        manager.restore(1, 99)
    assert exc.value.args == ("version not found",)
    with pytest.raises(ValueError) as exc:
        manager.export(1, "pdf")
    assert exc.value.args == ("unsupported format",)


@pytest.mark.parametrize("action,message", [
    (lambda: OrderBuilder().build(), "user is required"),
    (lambda: OrderBuilder().for_user(1, "a@b").build(), "items are required"),
    (lambda: OrderBuilder().for_user(0, "a@b").add_item("a", 1).build(), "invalid user_id"),
    (lambda: OrderBuilder().for_user(1, "bad").add_item("a", 1).build(), "invalid email"),
    (lambda: OrderBuilder().for_user(1, "a@b").add_item("a", 1).in_currency("GBP").build(), "unsupported currency"),
    (lambda: OrderBuilder().add_item("a", -1), "invalid item"),
    (lambda: PercentageDiscount(Decimal("-1")), "rate must be between 0 and 1"),
    (lambda: PercentageDiscount(Decimal("2")), "rate must be between 0 and 1"),
])
def test_exact_new_public_validation_messages(action, message):
    with pytest.raises(ValueError) as exc:
        action()
    assert exc.value.args == (message,)
