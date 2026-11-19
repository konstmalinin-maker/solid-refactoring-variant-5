"""Separated responsibility, still if/elif until the OCP step."""
import html
import json

from legacy.bad_code import Document, ScannedDocument


class ExportService:
    def __init__(self, reader):
        self.reader = reader

    def export(self, document_id, format):
        record = self.reader.get(document_id)
        if record is None:
            raise KeyError("document not found")
        document = ScannedDocument(record) if record["kind"] == "scan" else Document(record)
        if format == "txt":
            return document.get_text()
        if format == "html":
            return f'<h1>{html.escape(record["title"])}</h1><p>{html.escape(document.get_text())}</p>'
        if format == "json":
            return json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2)
        raise ValueError("unsupported format")
