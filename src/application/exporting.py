"""Orchestrates lookup and strategy selection; knows no concrete output formats."""
from src.domain.documents import make_document
from src.domain.exporters import ExporterRegistry


class ExportService:
    def __init__(self, reader, exporters=None):
        self.reader = reader
        self.exporters = exporters if exporters is not None else ExporterRegistry()

    def export(self, document_id, format):
        record = self.reader.get(document_id)
        if record is None:
            raise KeyError("document not found")
        document = make_document(record)
        return self.exporters.create(format).render(document)
