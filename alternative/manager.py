"""Same public API, independently orchestrated through functions and dispatch table."""
from pathlib import Path

from alternative import operations
from alternative.exports import default_exports
from solid.domain.documents import make_document
from solid.domain.validation import DocumentValidator
from solid.infrastructure.audit import FileAuditLog
from solid.infrastructure.catalog import CatalogRepository
from solid.infrastructure.store import JsonStore


class DocumentManager:
    def __init__(self, directory, repository=None, audit=None):
        self.repository = repository if repository is not None else CatalogRepository(JsonStore(directory))
        self.audit = audit if audit is not None else FileAuditLog(Path(directory) / "audit.log")
        self.validator, self.formats = DocumentValidator(), default_exports()

    def create(self, title, content, kind="text"):
        return operations.create(self.repository, self.validator, self.audit, title, content, kind)

    def get(self, document_id):
        return self.repository.get(document_id)

    def list_documents(self):
        return self.repository.list_documents()

    def update(self, document_id, title=None, content=None):
        return operations.update(self.repository, self.validator, self.audit, document_id, title, content)

    def delete(self, document_id):
        return operations.delete(self.repository, self.audit, document_id)

    def versions(self, document_id):
        return self.repository.versions(document_id)

    def restore(self, document_id, version):
        return operations.restore(self.repository, self, document_id, version)

    def search(self, query):
        query = query.casefold()
        return [row for row in self.list_documents()
                if query in row["title"].casefold() or query in row["content"].casefold()]

    def export(self, document_id, format):
        record = self.get(document_id)
        if record is None:
            raise KeyError("document not found")
        if not isinstance(format, str) or format not in self.formats:
            raise ValueError("unsupported format")
        return self.formats[format](make_document(record))

    def register_exporter(self, name, function):
        self.formats[name] = function
