from django.http import HttpRequest

from .content import ORGANISATION


def site(request: HttpRequest) -> dict:
    """Expose the organisation details to every template as ``site``."""
    return {"site": ORGANISATION}
