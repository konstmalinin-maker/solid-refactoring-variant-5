"""Неизменяемый контракт DocumentManager: один набор до/после/alternative."""
import json

import pytest


def test_create_normalizes_title_and_has_exact_fields(manager):
    assert manager.create("  Отчёт <1>  ", "Привет & мир") == {
        "id": 1, "title": "Отчёт <1>", "content": "Привет & мир", "kind": "text", "version": 1
    }
    assert manager.get(1) == manager.list_documents()[0]


def test_empty_content_is_allowed(manager):
    assert manager.create("Empty", "")["content"] == ""


@pytest.mark.parametrize("title,content,kind,message", [
    (None, "x", "text", "title must be a string"),
    ("   ", "x", "text", "title is required"),
    ("x" * 121, "x", "text", "title is too long"),
    ("x", None, "text", "content must be a string"),
    ("x", 123, "text", "content must be a string"),
    ("x", "x", "unknown", "unknown document kind"),
])
def test_invalid_create_has_no_side_effect(manager, title, content, kind, message):
    with pytest.raises(ValueError) as exc:
        manager.create(title, content, kind)
    assert str(exc.value) == message
    assert manager.list_documents() == []
    assert manager.create("valid", "")["id"] == 1


def test_title_boundary(manager):
    assert len(manager.create("x" * 120, "")["title"]) == 120


def test_ids_are_monotonic_and_sorted(manager):
    records = [manager.create(str(n), "text") for n in range(12)]
    manager.delete(5)
    assert manager.create("later", "")["id"] == 13
    assert [r["id"] for r in manager.list_documents()] == [r["id"] for r in records if r["id"] != 5] + [13]


def test_get_missing(manager):
    assert manager.get(999) is None
    assert manager.versions(999) == []
    assert manager.list_documents() == []


def test_update_and_version_snapshots(manager):
    original = manager.create("one", "old")
    assert manager.update(1, title=" two ", content="new") == {**original, "title": "two", "content": "new", "version": 2}
    assert manager.update(1, content="")["title"] == "two"
    assert manager.update(1)["version"] == 4
    assert manager.versions(1) == [original,
        {**original, "title": "two", "content": "new", "version": 2},
        {**original, "title": "two", "content": "", "version": 3},
        {**original, "title": "two", "content": "", "version": 4}]


def test_invalid_update_does_not_change_history(manager):
    original = manager.create("one", "old")
    with pytest.raises(ValueError, match="title is required"):
        manager.update(1, title=" ")
    assert manager.get(1) == original
    assert manager.versions(1) == [original]


def test_update_missing(manager):
    with pytest.raises(KeyError) as exc:
        manager.update(5, content="new")
    assert exc.value.args == ("document not found",)


def test_delete_keeps_history(manager):
    record = manager.create("one", "old")
    assert manager.delete(1) is True
    assert manager.delete(1) is False
    assert manager.get(1) is None
    assert manager.versions(1) == [record]
    with pytest.raises(KeyError, match="document not found"):
        manager.restore(1, 1)


def test_restore_creates_new_version(manager):
    record = manager.create("one", "old")
    manager.update(1, "two", "new")
    assert manager.restore(1, 1) == {**record, "version": 3}
    assert [r["version"] for r in manager.versions(1)] == [1, 2, 3]
    with pytest.raises(ValueError, match="version not found"):
        manager.restore(1, 9)


def test_results_are_defensive_copies(manager):
    created = manager.create("one", "old")
    created["title"] = "bad"
    manager.get(1)["title"] = "bad"
    manager.versions(1)[0]["title"] = "bad"
    manager.list_documents()[0]["title"] = "bad"
    assert manager.get(1)["title"] == "one"
    assert manager.versions(1)[0]["title"] == "one"


def test_search_title_content_and_unicode(manager):
    first = manager.create("Отчёт", "notes")
    second = manager.create("Other", "ОТЧЁТ inside")
    manager.create("excluded", "nothing")
    assert manager.search("отчёт") == [first, second]
    assert manager.search("NOTES") == [first]
    assert len(manager.search("")) == 3
    assert manager.search("absent") == []


def test_exports_exact_bytes(manager):
    record = manager.create('Title <&"', "Привет <&>")
    assert manager.export(1, "txt") == "Привет <&>"
    assert manager.export(1, "html") == '<h1>Title &lt;&amp;&quot;</h1><p>Привет &lt;&amp;&gt;</p>'
    assert manager.export(1, "json") == json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2)
    with pytest.raises(ValueError, match="unsupported format"):
        manager.export(1, "pdf")
    with pytest.raises(KeyError, match="document not found"):
        manager.export(999, "txt")


def test_scan_contract(manager):
    record = manager.create("scan", "image:abc", "scan")
    assert json.loads(manager.export(1, "json")) == record
    for format in ("txt", "html"):
        with pytest.raises(NotImplementedError) as exc:
            manager.export(1, format)
        assert str(exc.value) == "Scanned document has no text"


def test_reopen_persistence_and_exact_audit(manager, tmp_path):
    first = manager.create("one", "old")
    manager.update(1, content="new")
    other = type(manager)(tmp_path)
    assert other.get(1) == {**first, "content": "new", "version": 2}
    other.delete(1)
    assert manager.get(1) is None
    assert (tmp_path / "audit.log").read_text(encoding="utf-8") == "create:1\nupdate:1\ndelete:1\n"
