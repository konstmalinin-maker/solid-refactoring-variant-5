"""File audit adapter."""
from pathlib import Path


class FileAuditLog:
    def __init__(self, path):
        self.path = Path(path)

    def write(self, action, document_id):
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(f"{action}:{document_id}\n")
