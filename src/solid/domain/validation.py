"""Validation has one reason to change: accepted document input."""
class DocumentValidator:
    def validate(self, title, content, kind):
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
