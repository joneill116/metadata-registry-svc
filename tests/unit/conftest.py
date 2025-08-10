import pytest

# Shared fixtures, hooks, and plugins for pytest


def pytest_configure(config):
    # Register custom markers, plugins, etc. if needed
    pass


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    # Could be used to clear env vars, patch global state, etc.
    yield
    # Teardown logic if needed
