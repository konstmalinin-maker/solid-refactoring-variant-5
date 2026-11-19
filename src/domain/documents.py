"""All documents promise snapshots; only text-capable documents promise text."""
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


class Document(ABC):
    @abstractmethod
    def snapshot(self) -> dict: ...


@dataclass(frozen=True)
class StoredDocument(Document):
    record: dict

    def snapshot(self):
        return deepcopy(self.record)


@runtime_checkable
class TextContent(Protocol):
    def get_text(self) -> str: ...


class TextDocument(StoredDocument):
    def get_text(self):
        return self.record["content"]


class ScannedDocument(StoredDocument):
    """Has a snapshot, but makes no text-reading promise."""


def make_document(record):
    constructors = {"text": TextDocument, "scan": ScannedDocument}
    return constructors[record["kind"]](record)


def require_text(document):
    if not isinstance(document, TextContent):
        raise NotImplementedError("Scanned document has no text")
    return document.get_text()
