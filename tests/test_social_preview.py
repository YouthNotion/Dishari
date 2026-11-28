"""Link previews: the Open Graph / Twitter tags messengers read, and the share image."""

import re
import struct

import pytest
from django.contrib.staticfiles import finders
from django.test import override_settings

from core.content import ORGANISATION


def _meta(html: str, key: str) -> str:
    match = re.search(rf'<meta (?:property|name)="{re.escape(key)}" content="([^"]*)"', html)
    assert match, f"missing <meta> {key}"
    return match.group(1)


def test_share_tags_use_absolute_urls_and_the_wide_image(client):
    html = client.get("/").content.decode()

    assert _meta(html, "og:url") == "http://testserver/"
    assert _meta(html, "og:image") == "http://testserver/static/img/social-preview.png"
    assert _meta(html, "twitter:image") == _meta(html, "og:image")
    assert _meta(html, "twitter:card") == "summary_large_image"
    assert (_meta(html, "og:image:width"), _meta(html, "og:image:height")) == ("1200", "630")
    assert _meta(html, "og:description") == ORGANISATION.summary
    assert _meta(html, "description") == ORGANISATION.summary
    assert _meta(html, "og:image:alt")
    assert '<link rel="canonical" href="http://testserver/">' in html


@override_settings(SITE_URL="https://dishari.orgs.bd")
def test_site_url_setting_makes_previews_point_at_the_canonical_domain(client):
    """A link shared from a *.vercel.app address must still preview the real domain."""
    html = client.get("/").content.decode()

    assert _meta(html, "og:url") == "https://dishari.orgs.bd/"
    assert _meta(html, "og:image").startswith("https://dishari.orgs.bd/static/")
    assert '<link rel="canonical" href="https://dishari.orgs.bd/">' in html


def test_404_page_is_not_marked_canonical(client):
    html = client.get("/does-not-exist/").content.decode()

    assert 'rel="canonical"' not in html


def test_share_image_is_a_1200x630_png_small_enough_for_whatsapp():
    path = finders.find("img/social-preview.png")
    assert path, "static/img/social-preview.png is missing (run tools/make_social_image.py)"
    with open(path, "rb") as fh:
        header = fh.read(24)
        size = fh.seek(0, 2)

    assert header[:8] == b"\x89PNG\r\n\x1a\n"
    assert struct.unpack(">II", header[16:24]) == (1200, 630)
    assert size < 300 * 1024  # WhatsApp skips previews for large images


def test_summary_is_a_good_length_for_previews():
    assert 50 <= len(ORGANISATION.summary) <= 160


@pytest.mark.parametrize("value", ["dishari.orgs.bd", "ftp://dishari.orgs.bd"])
def test_site_url_without_http_scheme_is_rejected(monkeypatch, value):
    import importlib
    import sys

    from django.core.exceptions import ImproperlyConfigured

    monkeypatch.setenv("DJANGO_SITE_URL", value)
    sys.modules.pop("config.settings.base", None)
    try:
        with pytest.raises(ImproperlyConfigured, match="DJANGO_SITE_URL"):
            importlib.import_module("config.settings.base")
    finally:
        monkeypatch.delenv("DJANGO_SITE_URL")
        sys.modules.pop("config.settings.base", None)
        importlib.import_module("config.settings.base")
