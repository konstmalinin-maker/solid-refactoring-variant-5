"""Учебный legacy по описанию варианта 5; преподавательский исходник не приложен.

Маркеры SRP/OCP/LSP/ISP/DIP отмечают исходные проблемы. Файл не меняется
после фиксации baseline: ошибки поведения также являются частью контракта.
"""
import html
import json
from abc import ABC, abstractmethod
from pathlib import Path


class DocumentOperations(ABC):
    # ISP: чтение, запись, версии и экспорт сведены в один интерфейс.
    @abstractmethod
    def create(self, title, content, kind="text"): ...
    @abstractmethod
    def get(self, document_id): ...
    @abstractmethod
    def list_documents(self): ...
    @abstractmethod
    def update(self, document_id, title=None, content=None): ...
    @abstractmethod
    def delete(self, document_id): ...
    @abstractmethod
    def versions(self, document_id): ...
    @abstractmethod
    def export(self, document_id, format): ...


class Document:
    def __init__(self, record):
        self.record = record

    def get_text(self):
        return self.record["content"]


class ScannedDocument(Document):
    # LSP: базовый Document обещает текст; наследник вместо текста бросает ошибку.
    def get_text(self):
        raise NotImplementedError("Scanned document has no text")


class FileAuditLog:
    def __init__(self, path):
        self.path = Path(path)

    def write(self, action, document_id):
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(f"{action}:{document_id}\n")


class DocumentManager(DocumentOperations):
    # SRP: CRUD, валидация, версии, поиск, сериализация, ФС и аудит в одном классе.
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "documents.json"
        self.audit = FileAuditLog(self.directory / "audit.log")  # DIP: конкретная зависимость создаётся здесь.
        if not self.path.exists():
            self._save({"next_id": 1, "documents": {}, "history": {}})

    def _load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, state):
        self.path.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")

    def _validate(self, title, content, kind):
        if not isinstance(title, str):
            raise ValueError("title must be a string")
        if not title.strip():
            raise ValueError("title is required")
        if len(title.strip()) > 120:
            raise ValueError("title is too long")
        if not isinstance(content, str):
            raise ValueError("content must be a string")
        if kind not in ("text", "scan"):
            raise ValueError("unknown document kind")

    def create(self, title, content, kind="text"):
        self._validate(title, content, kind)
        state = self._load()
        document_id = state["next_id"]
        state["next_id"] += 1
        record = {"id": document_id, "title": title.strip(), "content": content, "kind": kind, "version": 1}
        state["documents"][str(document_id)] = record
        state["history"][str(document_id)] = [record.copy()]
        self._save(state)
        self.audit.write("create", document_id)
        return record.copy()

    def get(self, document_id):
        return self._load()["documents"].get(str(document_id))

    def list_documents(self):
        return sorted(self._load()["documents"].values(), key=lambda record: record["id"])

    def update(self, document_id, title=None, content=None):
        state = self._load()
        record = state["documents"].get(str(document_id))
        if record is None:
            raise KeyError("document not found")
        title = record["title"] if title is None else title
        content = record["content"] if content is None else content
        self._validate(title, content, record["kind"])
        record["title"] = title.strip()
        record["content"] = content
        record["version"] += 1  # Даже update без новых значений создаёт версию: сохраняем это поведение.
        state["history"][str(document_id)].append(record.copy())
        self._save(state)
        self.audit.write("update", document_id)
        return record.copy()

    def delete(self, document_id):
        state = self._load()
        if str(document_id) not in state["documents"]:
            return False
        del state["documents"][str(document_id)]
        self._save(state)
        self.audit.write("delete", document_id)
        return True  # История остаётся после удаления.

    def versions(self, document_id):
        return self._load()["history"].get(str(document_id), [])

    def restore(self, document_id, version):
        if self.get(document_id) is None:
            raise KeyError("document not found")
        for record in self.versions(document_id):
            if record["version"] == version:
                return self.update(document_id, record["title"], record["content"])
        raise ValueError("version not found")

    def search(self, query):
        query = query.casefold()
        result = []
        for record in self.list_documents():
            if query in record["title"].casefold() or query in record["content"].casefold():
                result.append(record)
        return result

    def export(self, document_id, format):
        record = self.get(document_id)
        if record is None:
            raise KeyError("document not found")
        document = ScannedDocument(record) if record["kind"] == "scan" else Document(record)
        # OCP: каждый новый формат требует изменения этого метода.
        if format == "txt":
            return document.get_text()
        elif format == "html":
            return f'<h1>{html.escape(record["title"])}</h1><p>{html.escape(document.get_text())}</p>'
        elif format == "json":
            return json.dumps(record, ensure_ascii=False, sort_keys=True, indent=2)
        raise ValueError("unsupported format")


class ReadOnlyDocumentView(DocumentOperations):
    # ISP: read-only реализация вынуждена объявлять недоступные операции.
    def __init__(self, manager):
        self.manager = manager
    def get(self, document_id):
        return self.manager.get(document_id)
    def list_documents(self):
        return self.manager.list_documents()
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
