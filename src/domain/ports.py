"""Small structural contracts: consumers request only the operations they use."""
from typing import Protocol


class DocumentReader(Protocol):
    def get(self, document_id): ...
    def list_documents(self): ...


class VersionReader(Protocol):
    def versions(self, document_id): ...


class DocumentWriter(Protocol):
    def create(self, title, content, kind): ...
    def update(self, document_id, title, content): ...
    def delete(self, document_id): ...


class DocumentRepository(DocumentReader, DocumentWriter, VersionReader, Protocol):
    """Composition for use cases that need the three capabilities together."""


class Audit(Protocol):
    def write(self, action, document_id): ...
