"""Function dispatch table instead of exporter Strategy subclasses."""
import html
import json

from solid.domain.documents import require_text


def text(document):
    return require_text(document)


def html_document(document):
    return f'<h1>{html.escape(document.snapshot()["title"])}</h1><p>{html.escape(require_text(document))}</p>'


def json_document(document):
    return json.dumps(document.snapshot(), ensure_ascii=False, sort_keys=True, indent=2)


def default_exports():
    return {"txt": text, "html": html_document, "json": json_document}
