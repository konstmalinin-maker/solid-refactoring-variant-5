"""JSON persistence, independent of document use cases."""
import json
from pathlib import Path


class JsonStore:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "documents.json"
        if not self.path.exists():
            self.save({"next_id": 1, "documents": {}, "history": {}})

    def load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, state):
        self.path.write_text(json.dumps(state, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
