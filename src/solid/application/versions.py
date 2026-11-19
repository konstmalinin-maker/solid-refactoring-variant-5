"""Version restore is a use case, not an export or storage format concern."""
class VersionService:
    def __init__(self, reader, commands):
        self.reader, self.commands = reader, commands

    def versions(self, document_id):
        return self.reader.versions(document_id)

    def restore(self, document_id, version):
        if self.reader.get(document_id) is None:
            raise KeyError("document not found")
        for record in self.versions(document_id):
            if record["version"] == version:
                return self.commands.update(document_id, record["title"], record["content"])
        raise ValueError("version not found")
