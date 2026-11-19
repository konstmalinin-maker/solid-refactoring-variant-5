"""Read-only client has no fake write/export methods or runtime permission stubs."""
from src.domain.ports import DocumentReader


class ReadOnlyDocumentView:
    def __init__(self, reader: DocumentReader):
        self.reader = reader

    def get(self, document_id):
        return self.reader.get(document_id)

    def list_documents(self):
        return self.reader.list_documents()
