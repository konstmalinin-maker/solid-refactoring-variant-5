"""Actual timeit measurements: identical persistent document work and 1000 exact PDF orders."""
import json
import platform
import random
import statistics
import tempfile
import timeit
from pathlib import Path

from alternative.manager import DocumentManager as FunctionalManager
from benchmarks.legacy_orders import LegacyOrderProcessor
from legacy.bad_code import DocumentManager as LegacyManager
from solid.compat import DocumentManager
from solid.extensions.builder import OrderBuilder
from solid.extensions.factory import RegisteredDiscountFactory
from solid.extensions.order_service import OrderService
from solid.infrastructure.order_repository import MemoryOrderRepository


def document_batch(manager_type, directory):
    manager = manager_type(directory)
    for i in range(1000):
        manager.create(f"Document {i}", f"Body {i}")
    rows = manager.list_documents()
    assert len(rows) == 1000 and rows[-1]["id"] == 1000
    assert all(row["version"] == 1 for row in rows)
    assert len((Path(directory) / "audit.log").read_text().splitlines()) == 1000


def run():
    measurements = {"legacy": [], "solid": [], "functional": []}
    classes = {"legacy": LegacyManager, "solid": DocumentManager, "functional": FunctionalManager}
    rng = random.Random(20261119)
    for trial in range(3):
        names = list(classes)
        rng.shuffle(names)
        for name in names:
            with tempfile.TemporaryDirectory(prefix="pr9-benchmark-") as directory:
                elapsed = timeit.Timer(lambda: document_batch(classes[name], directory)).timeit(number=1)
            measurements[name].append(elapsed)
            print("1000 documents:", trial + 1, name, f"{elapsed:.6f}s", flush=True)
    documents = {name: {"samples_s": values, "median_s": statistics.median(values)}
                 for name, values in measurements.items()}
    orders = [OrderBuilder().for_user(i + 1, "student@example.com", kind).add_item("Book", "125.50", 2).build()
              for i, kind in enumerate(["regular", "vip", "premium", "student", "unknown"] * 200)]
    def batch(factory):
        service = factory()
        receipts = [service.process_order(order) for order in orders]
        assert len(receipts) == 1000 and receipts[-1].id == 1000
        return [receipt.total for receipt in receipts]
    factories = {"legacy": LegacyOrderProcessor,
                 "solid": lambda: OrderService(MemoryOrderRepository(), RegisteredDiscountFactory())}
    assert batch(factories["legacy"]) == batch(factories["solid"])
    order_results = {}
    for name, factory in factories.items():
        values = timeit.repeat(lambda: batch(factory), repeat=9, number=1)
        order_results[name] = {"samples_s": values, "median_s": statistics.median(values)}
        print("1000 orders:", name, f"{statistics.median(values):.6f}s", flush=True)
    result = {"python": platform.python_version(), "platform": platform.system(), "count": 1000,
              "documents": documents, "orders": order_results,
              "notes": "Documents include identical JSON and audit I/O; order totals and receipt counts are equal. No network."}
    Path("docs/benchmark.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    run()
