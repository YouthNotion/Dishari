from django.contrib.staticfiles import finders

from core import content
from core.templatetags.site_tags import _ICON_PATHS


def test_phone_links_are_derived_from_display_number():
    org = content.ORGANISATION

    assert org.phone == "+880 1864-272727"
    assert org.phone_e164 == "+8801864272727"
    assert org.whatsapp_url == "https://wa.me/8801864272727"


def test_every_training_image_exists():
    for training in content.TRAININGS:
        assert finders.find(training.image), training.image


def test_every_service_icon_exists():
    for area in content.SERVICE_AREAS:
        assert area.icon in _ICON_PATHS, area.icon


def test_stylesheet_defines_both_themes():
    css_path = finders.find("css/site.css")
    with open(css_path, encoding="utf-8") as fh:
        css = fh.read()

    assert "color-scheme: light dark" in css
    assert ':root[data-theme="dark"]' in css
    assert "light-dark(" in css
