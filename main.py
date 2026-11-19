"""Composition root: runnable documents demo and exact PDF order examples A-C."""
import argparse
import json
from dataclasses import asdict

from solid.compat import DocumentManager
from solid.extensions.builder import OrderBuilder
from solid.extensions.factory import DiscountFactory, RegisteredDiscountFactory
from solid.extensions.order_service import OrderRepository, OrderService
from solid.infrastructure.container import Container
from solid.infrastructure.order_repository import MemoryOrderRepository


def build_container(directory):
    container = Container()
    repository = MemoryOrderRepository()
    container.register(DocumentManager, lambda: DocumentManager(directory))
    container.register(OrderRepository, lambda: repository)
    container.register(DiscountFactory, RegisteredDiscountFactory)
    container.register(OrderService, lambda: OrderService(container.resolve(OrderRepository),
                                                        container.resolve(DiscountFactory)))
    return container


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default="demo-data")
    args = parser.parse_args()
    container = build_container(args.directory)
    manager = container.resolve(DocumentManager)
    record = manager.create("Практика №9", "SOLID")
    manager.update(record["id"], content="SRP OCP LSP ISP DIP")
    print("DOCUMENT:", manager.export(record["id"], "json"))
    order = (OrderBuilder().for_user(5, "student@example.com", "student")
             .add_item("Book", "125.50", 2).with_notes("Learning SOLID")
             .deliver_to("Moscow").in_currency("RUB").build())
    receipt = container.resolve(OrderService).process_order(order)
    print("ORDER:", json.dumps(asdict(receipt), default=str, ensure_ascii=False))


if __name__ == "__main__":
    main()
