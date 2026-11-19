from pathlib import Path

import pytest

from solid.application.documents import DocumentService
from solid.application.exporting import ExportService
from solid.application.read_only import ReadOnlyDocumentView
from solid.compat import DocumentManager
from solid.domain.documents import Document, ScannedDocument, StoredDocument, TextContent, TextDocument, make_document
from solid.domain.exporters import Exporter, ExporterRegistry
from solid.domain.validation import DocumentValidator
from solid.infrastructure.catalog import CatalogRepository
from solid.infrastructure.memory import MemoryAudit, MemoryStore


@pytest.fixture
def memory():
    store, audit = MemoryStore(), MemoryAudit()
    repo = CatalogRepository(store)
    return repo, audit, DocumentService(repo, DocumentValidator(), audit)


def test_injected_dependencies_and_no_files(memory, tmp_path):
    repo, audit, commands = memory
    manager = DocumentManager(tmp_path / "unused", repository=repo, audit=audit)
    created = manager.create(" title ", "content")
    assert created == {"id": 1, "title": "title", "content": "content", "kind": "text", "version": 1}
    manager.update(1, "new", "value")
    manager.restore(1, 1)
    assert manager.get(1) == {**created, "version": 3}
    assert manager.delete(1) is True
    assert manager.delete(1) is False
    assert audit.events == [("create", 1), ("update", 1), ("update", 1), ("delete", 1)]
    assert not (tmp_path / "unused").exists()
    assert commands.repository is repo


def test_memory_store_copies_both_directions():
    store = MemoryStore()
    assert store.load() == {"next_id": 1, "documents": {}, "history": {}}
    state = {"next_id": 4, "documents": {"1": {"title": "x"}}, "history": {}}
    store.save(state)
    state["documents"]["1"]["title"] = "changed"
    loaded = store.load()
    loaded["documents"]["1"]["title"] = "changed again"
    assert store.load() == {"next_id": 4, "documents": {"1": {"title": "x"}}, "history": {}}


def test_narrow_read_only_view(memory):
    repo, _, commands = memory
    record = commands.create("one", "text")
    view = ReadOnlyDocumentView(repo)
    assert view.get(1) == record
    assert view.list_documents() == [record]
    assert not any(hasattr(view, name) for name in ("create", "update", "delete", "export", "versions"))


@pytest.mark.parametrize("kind,expected", [("text", TextDocument), ("scan", ScannedDocument)])
def test_lsp_snapshot_contract(kind, expected):
    record = {"id": 3, "title": "name", "content": "body", "kind": kind, "version": 2}
    document = make_document(record)
    assert type(document) is expected
    assert isinstance(document, Document)
    assert document.snapshot() == record
    document.snapshot()["title"] = "bad"
    assert document.snapshot() == record
    assert isinstance(document, TextContent) == (kind == "text")
    if kind == "text":
        assert document.get_text() == "body"
    else:
        assert not hasattr(document, "get_text")
    assert StoredDocument(record).snapshot() == record


def test_ocp_custom_strategy_without_service_edit(memory):
    repo, _, commands = memory
    commands.create("name", "body")
    class Markdown(Exporter):
        def render(self, document):
            return "# " + document.snapshot()["title"] + "\n" + document.get_text()
    registry = ExporterRegistry()
    registry.register("md", Markdown())
    service = ExportService(repo, registry)
    assert service.export(1, "md") == "# name\nbody"
    assert service.export(1, "txt") == "body"
    assert service.exporters is registry
    with pytest.raises(ValueError, match="unsupported format"):
        service.export(1, "unknown")


@pytest.mark.parametrize("format", [None, [], 42, "TXT", ""])
def test_unknown_export_type_retains_legacy_exception(memory, format):
    repo, _, commands = memory
    commands.create("a", "b")
    with pytest.raises(ValueError) as exc:
        ExportService(repo).export(1, format)
    assert str(exc.value) == "unsupported format"


def test_domain_and_application_import_no_storage_or_legacy():
    import ast
    for root in (Path("src/solid/domain"), Path("src/solid/application")):
        for path in root.glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.ImportFrom):
                    assert not (node.module or "").startswith(("legacy", "solid.infrastructure")), path
