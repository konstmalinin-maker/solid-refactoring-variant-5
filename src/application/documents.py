"""Document write use cases depend on ports; concrete construction belongs to the boundary."""
from src.domain.ports import Audit, DocumentRepository
from src.domain.validation import DocumentValidator


class DocumentService:
    def __init__(self, repository: DocumentRepository, validator: DocumentValidator, audit: Audit):
        self.repository, self.validator, self.audit = repository, validator, audit

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
