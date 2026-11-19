"""The fat interface remains visible here until the ISP step."""
from legacy.bad_code import DocumentOperations


class ReadOnlyDocumentView(DocumentOperations):
    def __init__(self, reader):
        self.reader = reader
    def get(self, document_id):
        return self.reader.get(document_id)
    def list_documents(self):
        return self.reader.list_documents()
    def create(self, *args):
        raise PermissionError("read only")
    def update(self, *args):
        raise PermissionError("read only")
    def delete(self, *args):
        raise PermissionError("read only")
    def versions(self, *args):
        raise PermissionError("read only")
    def export(self, *args):
        raise PermissionError("read only")
