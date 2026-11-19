"""F: independent functional use cases, sharing only ports' adapters and validation."""
def create(repository, validator, audit, title, content, kind):
    validator.validate(title, content, kind)
    result = repository.create(title.strip(), content, kind)
    audit.write("create", result["id"])
    return result


def update(repository, validator, audit, document_id, title, content):
    old = repository.get(document_id)
    if old is None:
        raise KeyError("document not found")
    title = old["title"] if title is None else title
    content = old["content"] if content is None else content
    validator.validate(title, content, old["kind"])
    result = repository.update(document_id, title.strip(), content)
    audit.write("update", document_id)
    return result


def delete(repository, audit, document_id):
    result = repository.delete(document_id)
    if result:
        audit.write("delete", document_id)
    return result


def restore(repository, commands, document_id, version):
    if repository.get(document_id) is None:
        raise KeyError("document not found")
    for record in repository.versions(document_id):
        if record["version"] == version:
            return commands.update(document_id, record["title"], record["content"])
    raise ValueError("version not found")
