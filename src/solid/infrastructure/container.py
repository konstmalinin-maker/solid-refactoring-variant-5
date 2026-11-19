"""C: explicit provider registration, resolution and reversible test overrides."""
from contextlib import contextmanager


class Container:
    def __init__(self):
        self.providers = {}

    def register(self, key, provider):
        self.providers[key] = provider

    def resolve(self, key):
        return self.providers[key]()

    @contextmanager
    def override(self, key, provider):
        original = self.providers[key]
        self.providers[key] = provider
        try:
            yield self
        finally:
            self.providers[key] = original
