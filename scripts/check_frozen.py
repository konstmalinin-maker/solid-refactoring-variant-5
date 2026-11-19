"""Audit the actual Git baseline, not editable expected-output fixtures."""
import hashlib
import json
import subprocess
from pathlib import Path

BASELINE = "ce98fb0"
paths = ["conftest.py", "tests_before/__init__.py", "tests_before/test_characterization.py",
         "tests_before/test_legacy_violations.py", "legacy/bad_code.py"]
results = {}
for name in paths:
    original = subprocess.check_output(["git", "show", BASELINE + ":" + name])
    current = Path(name).read_bytes()
    assert current == original, "Frozen file changed: " + name
    results[name] = hashlib.sha256(current).hexdigest()
print("FROZEN CONTRACT PASSED: legacy and characterization files are byte-identical to", BASELINE)
print(json.dumps(results, indent=2))
