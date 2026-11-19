"""Factory Method: creation is overridable; registry extends its default implementation."""
from abc import ABC, abstractmethod
from decimal import Decimal

from solid.extensions.discounts import NoDiscount, PercentageDiscount


class DiscountFactory(ABC):
    @abstractmethod
    def create(self, user_type): ...


class RegisteredDiscountFactory(DiscountFactory):
    def __init__(self):
        self.providers = {
            "regular": lambda: PercentageDiscount(Decimal("0.05")),
            "vip": lambda: PercentageDiscount(Decimal("0.10")),
            "premium": lambda: PercentageDiscount(Decimal("0.15")),
            "student": lambda: PercentageDiscount(Decimal("0.20")),
        }

    def register(self, name):
        def decorate(provider):
            self.providers[name] = provider
            return provider
        return decorate

    def create(self, user_type):
        return self.providers.get(user_type, NoDiscount)()
