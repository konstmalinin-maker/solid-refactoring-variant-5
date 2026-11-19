"""Repository owns storage schema and revision snapshots, not validation or export."""
class CatalogRepository:
    def __init__(self, store):
        self.store = store

    def get(self, document_id):
        return self.store.load()["documents"].get(str(document_id))

    def list_documents(self):
        return sorted(self.store.load()["documents"].values(), key=lambda row: row["id"])

    def versions(self, document_id):
        return self.store.load()["history"].get(str(document_id), [])

    def create(self, title, content, kind):
        state = self.store.load()
        document_id = state["next_id"]
        state["next_id"] += 1
        record = {"id": document_id, "title": title, "content": content, "kind": kind, "version": 1}
        state["documents"][str(document_id)] = record
        state["history"][str(document_id)] = [record.copy()]
        self.store.save(state)
        return record.copy()

    def update(self, document_id, title, content):
        state = self.store.load()
        record = state["documents"][str(document_id)]
        record.update(title=title, content=content, version=record["version"] + 1)
        state["history"][str(document_id)].append(record.copy())
        self.store.save(state)
        return record.copy()

    def delete(self, document_id):
        state = self.store.load()
        if str(document_id) not in state["documents"]:
            return False
        del state["documents"][str(document_id)]
        self.store.save(state)
        return True
