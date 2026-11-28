from django.conf import settings
from django.http import HttpRequest

from .content import ORGANISATION


def site(request: HttpRequest) -> dict[str, object]:
    """Expose the organisation as ``site``, plus absolute URLs for link previews.

    ``site_url`` is settings.SITE_URL when configured (the canonical domain), otherwise
    the scheme and host of the current request. ``canonical_url`` is that plus the path.
    """
    base = settings.SITE_URL or f"{request.scheme}://{request.get_host()}"
    return {
        "site": ORGANISATION,
        "site_url": base,
        "canonical_url": base + request.path,
    }
