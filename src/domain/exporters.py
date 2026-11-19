"""Export strategies: extending formats does not change ExportService."""
import html
import json
from abc import ABC, abstractmethod


class Exporter(ABC):
    @abstractmethod
    def render(self, document): ...


class TextExporter(Exporter):
    def render(self, document):
        return document.get_text()


class HtmlExporter(Exporter):
    def render(self, document):
        return f'<h1>{html.escape(document.record["title"])}</h1><p>{html.escape(document.get_text())}</p>'


class JsonExporter(Exporter):
    def render(self, document):
        return json.dumps(document.record, ensure_ascii=False, sort_keys=True, indent=2)


class ExporterRegistry:
    def __init__(self):
        self.exporters = {"txt": TextExporter(), "html": HtmlExporter(), "json": JsonExporter()}

    def register(self, name, exporter):
        self.exporters[name] = exporter

    def create(self, format):
        if not isinstance(format, str):
            raise ValueError("unsupported format")
        try:
            return self.exporters[format]
        except KeyError:
            raise ValueError("unsupported format") from None
