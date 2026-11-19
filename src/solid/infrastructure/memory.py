"""Replace persistent storage and audit without replacing business use cases."""
from copy import deepcopy


class MemoryStore:
    def __init__(self):
        self.state = {"next_id": 1, "documents": {}, "history": {}}

    def load(self):
        return deepcopy(self.state)

    def save(self, state):
        self.state = deepcopy(state)


class MemoryAudit:
    def __init__(self):
        self.events = []

    def write(self, action, document_id):
        self.events.append((action, document_id))
