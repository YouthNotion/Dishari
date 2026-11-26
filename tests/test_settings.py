import importlib
import sys

import pytest
from django.core.exceptions import ImproperlyConfigured

SECRET = "x" * 50
VERCEL_ENV = {
    "VERCEL": "1",
    "VERCEL_URL": "dishari-abc123.vercel.app",
    "VERCEL_PROJECT_PRODUCTION_URL": "dishari.vercel.app",
    "DJANGO_SECRET_KEY": SECRET,
}


@pytest.fixture
def import_prod(monkeypatch):
    for name in (*VERCEL_ENV, "VERCEL_BRANCH_URL", "DJANGO_BEHIND_TLS_PROXY"):
        monkeypatch.delenv(name, raising=False)

    def _import(**env):
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        sys.modules.pop("config.settings.prod", None)
        return importlib.import_module("config.settings.prod")

    yield _import
    sys.modules.pop("config.settings.prod", None)


def test_prod_requires_secret_key(import_prod):
    with pytest.raises(ImproperlyConfigured):
        import_prod()


def test_prod_is_hardened(import_prod):
    prod = import_prod(DJANGO_SECRET_KEY=SECRET)

    assert prod.DEBUG is False
    assert prod.SECURE_SSL_REDIRECT is True
    assert prod.CSRF_COOKIE_SECURE is True
    assert prod.SECURE_HSTS_SECONDS > 0
    assert prod.DATABASES == {}
    assert not hasattr(prod, "SECURE_PROXY_SSL_HEADER")


def test_vercel_hosts_and_proxy(import_prod):
    prod = import_prod(**VERCEL_ENV)

    assert {"dishari-abc123.vercel.app", "dishari.vercel.app"} <= set(prod.ALLOWED_HOSTS)
    assert "https://dishari.vercel.app" in prod.CSRF_TRUSTED_ORIGINS
    assert prod.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")
