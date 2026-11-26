"""Settings used by the pytest suite."""

from .base import *  # noqa: F403

DEBUG = False
SECRET_KEY = "test-secret-key"  # noqa: S105
ALLOWED_HOSTS = ["testserver", "localhost"]


STORAGES = {
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# Serve static files via finders without needing collectstatic.
WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = True
