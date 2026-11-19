"""Comparable metrics: actual Radon ranks, weighted MI and routine source ranges."""
import argparse
import ast
import json
from pathlib import Path
from statistics import mean

from radon.complexity import cc_rank, cc_visit
from radon.metrics import mi_rank, mi_visit
from radon.raw import analyze


def measure(paths, main_class):
    files = sorted({p for root in paths for p in ([Path(root)] if Path(root).is_file() else Path(root).rglob("*.py"))})
    entries, complexity, lengths, classes, main_methods = [], [], [], 0, 0
    for path in files:
        source = path.read_text()
        raw = analyze(source)
        if not raw.sloc:
            continue
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                lengths.append(node.end_lineno - node.lineno + 1)
            if isinstance(node, ast.ClassDef):
                classes += 1
                if node.name == main_class:
                    main_methods += sum(isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) for m in node.body)
        for block in cc_visit(source):
            routines = block.methods if hasattr(block, "methods") else [block]
            complexity.extend(item.complexity for item in routines)
        mi = mi_visit(source, multi=True)
        entries.append({"file": str(path), "sloc": raw.sloc, "mi": round(mi, 4), "rank": mi_rank(mi),
                        "imports": sum(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree))})
    sloc = sum(item["sloc"] for item in entries)
    return {"average_cc": round(mean(complexity), 4), "cc_rank": cc_rank(mean(complexity)),
            "maximum_cc": max(complexity), "weighted_mi": round(sum(e["mi"] * e["sloc"] for e in entries) / sloc, 4),
            "minimum_mi": min(e["mi"] for e in entries), "average_method_loc": round(mean(lengths), 4),
            "maximum_method_loc": max(lengths), "main_class": main_class, "main_class_methods": main_methods,
            "classes": classes, "sloc": sloc, "files": entries}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", action="append", required=True)
    parser.add_argument("--main-class", default="DocumentService")
    parser.add_argument("--output", required=True)
    parser.add_argument("--gate", action="store_true")
    args = parser.parse_args()
    result = measure(args.path, args.main_class)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "files"}, indent=2))
    if args.gate and (result["average_cc"] > 10 or result["weighted_mi"] < 60 or result["minimum_mi"] <= 19):
        raise SystemExit("QUALITY GATE FAILED: average CC must be <=10; weighted MI >=60 and every file rank A (MI >19)")
    if args.gate:
        print("QUALITY GATE PASSED: average CC <=10; weighted MI >=60 and every file rank A (MI >19)")


if __name__ == "__main__":
    main()
