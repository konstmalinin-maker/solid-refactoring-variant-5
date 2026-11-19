import importlib

import pytest


def pytest_addoption(parser):
    parser.addoption("--backend", default="legacy", choices=["legacy", "refactored", "alternative"])


@pytest.fixture
def manager(tmp_path, request):
    modules = {"legacy": "legacy.bad_code", "refactored": "src.compat", "alternative": "alternative.manager"}
    return importlib.import_module(modules[request.config.getoption("--backend")]).DocumentManager(tmp_path)
