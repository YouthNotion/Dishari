"""Production settings. All secrets come from the environment.

Works on any WSGI host (gunicorn behind a proxy) and on Vercel, which is
detected through the ``VERCEL`` system environment variable.
"""

import os

from .base import *  # noqa: F403
from .base import env, env_bool

DEBUG = False
SECRET_KEY = env("DJANGO_SECRET_KEY")

ON_VERCEL = bool(os.environ.get("VERCEL"))

# --- Hosts -------------------------------------------------------------------

if ON_VERCEL:
    # Vercel's system env vars hold bare hostnames (no scheme).
    _vercel_hosts = [
        host
        for name in ("VERCEL_PROJECT_PRODUCTION_URL", "VERCEL_URL", "VERCEL_BRANCH_URL")
        if (host := os.environ.get(name))
    ]
    ALLOWED_HOSTS = [*ALLOWED_HOSTS, *_vercel_hosts]  # noqa: F405
    CSRF_TRUSTED_ORIGINS = [*CSRF_TRUSTED_ORIGINS, *(f"https://{h}" for h in _vercel_hosts)]  # noqa: F405

# --- HTTPS -------------------------------------------------------------------

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = int(env("DJANGO_SECURE_HSTS_SECONDS", "3600"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", False)

# Trust X-Forwarded-Proto only behind a TLS-terminating proxy (Vercel always is one).
if ON_VERCEL or env_bool("DJANGO_BEHIND_TLS_PROXY", False):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Let plain-HTTP health checks from the load balancer through.
SECURE_REDIRECT_EXEMPT = [r"^healthz$"]
