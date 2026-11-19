"""Only document write use cases. DIP will remove concrete construction in step 5."""
from pathlib import Path

from src.domain.validation import DocumentValidator
from src.infrastructure.audit import FileAuditLog
from src.infrastructure.catalog import CatalogRepository
from src.infrastructure.store import JsonStore


class DocumentService:
    def __init__(self, directory):
        self.repository = CatalogRepository(JsonStore(directory))
        self.validator = DocumentValidator()
        self.audit = FileAuditLog(Path(directory) / "audit.log")

    def create(self, title, content, kind="text"):
        self.validator.validate(title, content, kind)
        result = self.repository.create(title.strip(), content, kind)
        self.audit.write("create", result["id"])
        return result

    def update(self, document_id, title=None, content=None):
        record = self.repository.get(document_id)
        if record is None:
            raise KeyError("document not found")
        title = record["title"] if title is None else title
        content = record["content"] if content is None else content
        self.validator.validate(title, content, record["kind"])
        result = self.repository.update(document_id, title.strip(), content)
        self.audit.write("update", document_id)
        return result

    def delete(self, document_id):
        deleted = self.repository.delete(document_id)
        if deleted:
            self.audit.write("delete", document_id)
        return deleted
