"""Read operations; does not write files or create versions."""
class DocumentQueries:
    def __init__(self, reader):
        self.reader = reader

    def get(self, document_id):
        return self.reader.get(document_id)

    def list_documents(self):
        return self.reader.list_documents()

    def search(self, query):
        query = query.casefold()
        return [row for row in self.list_documents()
                if query in row["title"].casefold() or query in row["content"].casefold()]
