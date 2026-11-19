"""Stable external API; delegates to focused services, retains no business rules."""
from src.application.documents import DocumentService
from src.application.exporting import ExportService
from src.application.queries import DocumentQueries
from src.application.versions import VersionService


class DocumentManager:
    def __init__(self, directory):
        self.commands = DocumentService(directory)
        self.reader = DocumentQueries(self.commands.repository)
        self.revisions = VersionService(self.commands.repository, self.commands)
        self.exporter = ExportService(self.reader)

    def create(self, title, content, kind="text"):
        return self.commands.create(title, content, kind)

    def get(self, document_id):
        return self.reader.get(document_id)

    def list_documents(self):
        return self.reader.list_documents()

    def search(self, query):
        return self.reader.search(query)

    def update(self, document_id, title=None, content=None):
        return self.commands.update(document_id, title, content)

    def delete(self, document_id):
        return self.commands.delete(document_id)

    def versions(self, document_id):
        return self.revisions.versions(document_id)

    def restore(self, document_id, version):
        return self.revisions.restore(document_id, version)

    def export(self, document_id, format):
        return self.exporter.export(document_id, format)
