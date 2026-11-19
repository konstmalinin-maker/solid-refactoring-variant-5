"""Readable views calculated from saved measurements and mutmut metadata."""
import json
import sys
from pathlib import Path


def read(name):
    return json.loads(Path("docs/" + name).read_text())


mode = sys.argv[1]
if mode == "metrics":
    before, after = read("metrics-before.json"), read("metrics-core-final.json")
    print(f'{"METRIC":32} {"LEGACY":>12} {"SOLID CORE":>12}')
    for name in ("average_cc", "weighted_mi", "average_method_loc", "maximum_method_loc", "main_class_methods", "classes", "sloc"):
        print(f'{name:32} {str(before[name]):>12} {str(after[name]):>12}')
    print("Legacy core and document core only; extra A-C order examples excluded.")
    print("MI uses actual Radon values; CC counts functions/methods, not class aggregates twice.")
elif mode == "alternative":
    data = read("alternative-comparison.json")
    print(f'{"METRIC":30} {"STRATEGY + PORTS":>18} {"FUNCTION DISPATCH":>18}')
    for name in ("average_cc", "weighted_mi", "maximum_method_loc", "classes", "sloc"):
        print(f'{name:30} {str(data["primary"][name]):>18} {str(data["functional"][name]):>18}')
    print(data["scope"]["note"])
else:
    data = read("benchmark.json")
    print("ACTUAL timeit | Python", data["python"], "|", data["platform"], "| count =", data["count"])
    for kind in ("documents", "orders"):
        print("\n1000", kind, "- median seconds")
        for name, value in data[kind].items():
            print(f'{name:16} {value["median_s"]:.6f} | samples = {len(value["samples_s"])}')
        base = data[kind]["legacy"]["median_s"]
        for name, value in data[kind].items():
            if name != "legacy":
                print(f'{name}: {(value["median_s"] / base - 1)*100:+.2f}% relative to legacy')
    print("\n" + data["notes"])
