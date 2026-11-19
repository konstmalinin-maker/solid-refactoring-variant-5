#!/bin/bash
set -e
cd /workspace/solid-refactoring-variant-5
source /workspace/venv-pr9/bin/activate
case "$1" in
legacy|srp|ocp|lsp|isp|dip) python -m scripts.show_steps "$1" ;;
before) set -x; pytest tests_before --backend=legacy -q --cov=legacy --cov-fail-under=80 ;;
before-metrics) set -x; radon cc legacy/bad_code.py -a -s | tail -7; radon mi legacy/bad_code.py -s; python -m scripts.show_results metrics ;;
after) set -x; pytest tests_before tests_after -q --cov=solid --cov-fail-under=85 ;;
after-metrics) set -x; radon cc src/solid -a -s | tail -7; python scripts/metrics.py --path src/solid --main-class DocumentService --output /workspace/pr9-data/native-final-metrics.json --gate ;;
frozen) set -x; python scripts/check_frozen.py; git log --oneline --reverse | head -10 ;;
structure) set -x; rg --files src alternative | sort ;;
factory) set -x; pytest tests_after/test_extensions.py -k 'factory or registration or discount' -v --tb=short ;;
builder) set -x; pytest tests_after/test_extensions.py -k 'builder or user or email or currency' -v --tb=short ;;
container) set -x; pytest tests_after/test_extensions.py -k 'container' -v --tb=short ;;
mutation) set -x; python scripts/mutation_summary.py --output /workspace/pr9-data/native-mutation.json --gate ;;
weak) set -x; cat /workspace/pr9-data/weak-coverage.txt; python -c 'import json; d=json.load(open("/workspace/pr9-data/weak-coverage.json")); print("ACTUAL WEAK LINE COVERAGE:",d["totals"]["percent_covered"],"percent"); print("Covered:",d["totals"]["covered_lines"],"/",d["totals"]["num_statements"],"statements")'; python scripts/mutation_summary.py --directory /workspace/pr9-weak-lab/mutants --output /workspace/pr9-data/native-weak.json ;;
mutants) set -x; cat /workspace/pr9-data/surviving-diffs.txt ;;
alternative) set -x; pytest tests_before --backend=alternative -q; python -m scripts.show_results alternative ;;
benchmark) set -x; python -m scripts.show_results benchmark ;;
demo) set -x; python main.py --directory /workspace/pr9-native/documents ;;
ci-positive) set -x; cat /workspace/pr9-data/ci-positive.txt ;;
ci-negative) set -x; cat /workspace/pr9-data/ci-negative.txt ;;
pr) set -x; cat /workspace/pr9-data/pr-final.txt ;;
esac
