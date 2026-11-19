"""Create an isolated mutation experiment; production source is copied unchanged."""
import argparse
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", required=True)
    args = parser.parse_args()
    target = Path(args.directory)
    target.mkdir(parents=True, exist_ok=True)
    for name in ("src/solid/__init__.py", "src/solid/extensions/__init__.py", "src/solid/extensions/discounts.py"):
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(name, destination)
    (target / "tests").mkdir(exist_ok=True)
    shutil.copyfile("quality_demo/test_weak.py", target / "tests/test_weak.py")
    (target / "pyproject.toml").write_text('''[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
[tool.mutmut]
paths_to_mutate = ["src/solid/extensions/discounts.py"]
tests_dir = ["tests"]
also_copy = ["src/solid/__init__.py", "src/solid/extensions/__init__.py"]
max_stack_depth = -1
''')
    print("Weak experiment uses byte-identical discounts.py:", target)


if __name__ == "__main__":
    main()
