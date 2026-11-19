"""Display actual source excerpts from Git commits; no invented execution output."""
import ast
import subprocess
import sys
from pathlib import Path

from pygments import highlight
from pygments.formatters import Terminal256Formatter
from pygments.lexers import PythonLexer


def fragment(ref, path, name):
    source = subprocess.check_output(["git", "show", ref + ":" + path], text=True) if ref else Path(path).read_text()
    tree = ast.parse(source)
    node = next(n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)
    lines = source.splitlines()
    return "\n".join(lines[node.lineno - 1:node.end_lineno])


def show(label, ref, path, name, limit=None):
    text = fragment(ref, path, name)
    if limit:
        text = "\n".join(text.splitlines()[:limit])
    print(label + " | " + path + " | " + (ref or "working tree"))
    print(highlight(text, PythonLexer(), Terminal256Formatter(style="monokai")), end="")


step = sys.argv[1]
if step == "legacy":
    show("SRP + DIP: mixed responsibilities and direct file audit", "80b1bde", "legacy/bad_code.py", "DocumentManager", 10)
    show("LSP: subclass breaks text promise", "80b1bde", "legacy/bad_code.py", "ScannedDocument")
    show("OCP: export if/elif", "80b1bde", "legacy/bad_code.py", "export", 1)
    # DocumentOperations declares export first: display actual format branches by line range.
    lines = Path("legacy/bad_code.py").read_text().splitlines()
    start = next(i for i,line in enumerate(lines) if '# OCP:' in line)
    print(highlight("\n".join(lines[start:start+9]), PythonLexer(), Terminal256Formatter(style="monokai")), end="")
    show("ISP: read-only class still declares write operations", "80b1bde", "legacy/bad_code.py", "ReadOnlyDocumentView", 9)
elif step == "srp":
    show("BEFORE SRP", "80b1bde", "legacy/bad_code.py", "DocumentManager", 9)
    print("AFTER SRP: DocumentService, DocumentQueries, VersionService, ExportService, CatalogRepository, FileAuditLog")
    show("Focused write use case", "b21fa1c", "src/application/documents.py", "DocumentService", 20)
elif step == "ocp":
    source = subprocess.check_output(["git", "show", "80b1bde:legacy/bad_code.py"], text=True).splitlines()
    start = next(i for i,line in enumerate(source) if '# OCP:' in line)
    print("BEFORE OCP | actual legacy export branches")
    print(highlight("\n".join(source[start:start+9]), PythonLexer(), Terminal256Formatter(style="monokai")), end="")
    show("AFTER OCP: strategy", "7cc463d", "src/domain/exporters.py", "TextExporter")
    show("AFTER OCP: extensible registry", "7cc463d", "src/domain/exporters.py", "ExporterRegistry")
elif step == "lsp":
    show("BEFORE LSP", "80b1bde", "legacy/bad_code.py", "ScannedDocument")
    for name in ("Document", "StoredDocument", "TextContent", "TextDocument", "ScannedDocument", "require_text"):
        show("AFTER LSP", None, "src/solid/domain/documents.py", name)
elif step == "isp":
    show("BEFORE ISP", "80b1bde", "legacy/bad_code.py", "ReadOnlyDocumentView", 13)
    show("AFTER ISP: only read capability", None, "src/solid/domain/ports.py", "DocumentReader")
    show("AFTER ISP: no fake create/update/delete", None, "src/solid/application/read_only.py", "ReadOnlyDocumentView")
elif step == "dip":
    show("BEFORE DIP: concrete dependencies in business service", "b21fa1c", "src/application/documents.py", "DocumentService", 6)
    show("AFTER DIP: injected ports", None, "src/solid/application/documents.py", "DocumentService", 12)
    show("Replaceable storage adapter", None, "src/solid/infrastructure/memory.py", "MemoryStore")
else:
    raise SystemExit("unknown step")
print("\nREGRESSION CHECK (original command log):")
p = Path("/workspace/pr9-data/step-" + step + ".txt")
if p.exists():
    print(p.read_text())
