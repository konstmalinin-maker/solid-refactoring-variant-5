"""Measure explicit, documented source scopes without treating shared adapters as free."""
import json
from pathlib import Path

from scripts.metrics import measure

core = json.loads(Path("docs/metrics-core.json").read_text())
primary = [item["file"].replace("src/", "src/solid/", 1) for item in core["files"]]
shared = [name for name in primary if "/infrastructure/" in name or name.endswith(("domain/documents.py", "domain/validation.py"))]
result = {"primary": measure(primary, "DocumentService"),
          "functional": measure(["alternative", *shared], "DocumentManager"),
          "scope": {"primary": primary, "functional_shared": shared,
                    "note": "Full variant 5 core vs independent functions plus every shared adapter/model. A-C order examples excluded."}}
Path("docs/metrics-core-final.json").write_text(json.dumps(result["primary"], indent=2) + "\n")
Path("docs/alternative-comparison.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({name:{k:v for k,v in result[name].items() if k != "files"}
                  for name in ("primary", "functional")}, indent=2))
