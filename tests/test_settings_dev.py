import importlib
import sys

import pytest


@pytest.fixture
def import_dev(monkeypatch):
    monkeypatch.delenv("DJANGO_ALLOWED_HOSTS", raising=False)

    def _import(**env):
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        sys.modules.pop("config.settings.dev", None)
        return importlib.import_module("config.settings.dev")

    yield _import
    sys.modules.pop("config.settings.dev", None)


def test_dev_allows_localhost_by_default(import_dev):
    dev = import_dev()

    assert dev.ALLOWED_HOSTS == ["localhost", "127.0.0.1", "[::1]"]


def test_dev_allowed_hosts_env_adds_to_localhost(import_dev):
    """Regression for #5: setting DJANGO_ALLOWED_HOSTS (e.g. from .env.example) must not
    remove localhost, or the dev server rejects every request with 400."""
    dev = import_dev(DJANGO_ALLOWED_HOSTS="example.org,192.168.1.20,localhost")

    assert dev.ALLOWED_HOSTS == ["localhost", "127.0.0.1", "[::1]", "example.org", "192.168.1.20"]
