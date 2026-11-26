"""Local development settings. Never use in production."""

from .base import *  # noqa: F403
from .base import env, env_list

DEBUG = True
SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-insecure-secret-key-do-not-use-in-production")  # noqa: S105
# Local hosts are always allowed in dev; DJANGO_ALLOWED_HOSTS only *adds* to them
# (e.g. a LAN IP for testing on a phone), so an env file can't lock you out of localhost.
_LOCAL_HOSTS = ["localhost", "127.0.0.1", "[::1]"]
ALLOWED_HOSTS = list(dict.fromkeys([*_LOCAL_HOSTS, *env_list("DJANGO_ALLOWED_HOSTS")]))

# Serve un-hashed static files straight from disk without collectstatic.
STORAGES = {
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Serve static files via finders without needing collectstatic.
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True

# Reload the browser automatically when templates, static files or Python code change.
# "runserver_nostatic" lets WhiteNoise (not runserver) serve static files, so dev
# matches production and honours WHITENOISE_MAX_AGE below.
INSTALLED_APPS = ["whitenoise.runserver_nostatic", *INSTALLED_APPS, "django_browser_reload"]  # noqa: F405
MIDDLEWARE = [*MIDDLEWARE, "django_browser_reload.middleware.BrowserReloadMiddleware"]  # noqa: F405

# Make the browser re-check static files on every load, so edited images/CSS show up
# immediately instead of a stale cached copy.
WHITENOISE_MAX_AGE = 0
