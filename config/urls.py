from django.conf import settings
from django.urls import include, path

urlpatterns = [
    path("", include("core.urls")),
]

# Dev only: live browser reload (see config/settings/dev.py).
if "django_browser_reload" in settings.INSTALLED_APPS:
    urlpatterns += [path("__reload__/", include("django_browser_reload.urls"))]
