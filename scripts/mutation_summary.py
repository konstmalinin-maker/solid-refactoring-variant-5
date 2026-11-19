"""Read actual mutmut metadata; fail on missing tests or >=10% non-killed mutants."""
import argparse
import json
from collections import Counter
from pathlib import Path

from mutmut.__main__ import status_by_exit_code


def summarize(directory):
    files, statuses, survivors = {}, Counter(), []
    for path in sorted(Path(directory).rglob("*.py.meta")):
        outcomes = json.loads(path.read_text())["exit_code_by_key"]
        counts = Counter(status_by_exit_code.get(value, str(value)) for value in outcomes.values())
        files[str(path.relative_to(directory))] = dict(counts)
        statuses.update(counts)
        survivors.extend(key for key, value in outcomes.items() if value == 0)
    total = sum(statuses.values())
    if not total:
        raise SystemExit("No mutmut metadata found")
    return {"total": total, "counts": dict(statuses), "survivor_percent": 100 * statuses["survived"] / total,
            "non_killed_percent": 100 * (total - statuses["killed"]) / total,
            "files": files, "surviving_ids": survivors}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default="mutants")
    parser.add_argument("--output", required=True)
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args()
    result = summarize(args.directory)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("files", "surviving_ids")}, indent=2))
    if args.gate and (result["non_killed_percent"] >= 10 or result["counts"].get("no tests", 0)):
        raise SystemExit("MUTATION GATE FAILED")
    if args.gate:
        print("MUTATION GATE PASSED: <10% survivors and <10% all non-killed; no untested functions")


if __name__ == "__main__":
    main()
