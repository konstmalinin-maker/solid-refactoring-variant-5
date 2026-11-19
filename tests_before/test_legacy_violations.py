"""Исходные антипримеры остаются в legacy; новые контракты проверяются отдельно."""
import pytest

from legacy.bad_code import Document, DocumentManager, ReadOnlyDocumentView, ScannedDocument


def test_original_lsp_violation():
    assert Document({"content": "text"}).get_text() == "text"
    with pytest.raises(NotImplementedError, match="Scanned document has no text"):
        ScannedDocument({"content": "image"}).get_text()


def test_original_fat_interface(tmp_path):
    manager = DocumentManager(tmp_path)
    view = ReadOnlyDocumentView(manager)
    item = manager.create("A", "B")
    assert view.get(1) == item
    assert view.list_documents() == [item]
    for method in (view.create, view.update, view.delete, view.versions, view.export):
        with pytest.raises(PermissionError, match="read only"):
            method()
