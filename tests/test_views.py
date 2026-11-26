from django.urls import reverse


def _home(client) -> str:
    response = client.get(reverse("core:home"))
    assert response.status_code == 200
    return response.content.decode()


def test_home_renders_content(client):
    html = _home(client)

    assert "Dishari" in html
    assert "Dream of New Earth" in html
    for text in ("Project Sandhyatara", "Legal activities", "Hand embroidery"):
        assert text in html
    assert 'src="/static/img/logo.png"' in html
    assert 'src="/static/img/training/sewing.jpg"' in html


def test_contact_details(client):
    html = _home(client)

    assert 'href="tel:+8801864272727"' in html
    assert 'href="https://wa.me/8801864272727"' in html
    assert 'href="mailto:dishari.org2023@gmail.com"' in html
    assert 'href="https://www.facebook.com/share/1FNyF5h8Qc/"' in html


def test_removed_content_stays_removed(client):
    html = _home(client).lower()

    for gone in (
        "our team",
        'id="team',
        "sawe",  # old organisation's links and email
        "1616535404",  # old phone number
        "hero.jpg",  # old hero wallpaper
        "topbar",  # separate contact bar above the nav
    ):
        assert gone not in html, gone


def test_security_headers(client):
    response = client.get("/")

    csp = response.headers["Content-Security-Policy"]
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_custom_404(client):
    response = client.get("/does-not-exist/")

    assert response.status_code == 404
    assert "couldn’t find that page" in response.content.decode()


def test_healthz(client):
    response = client.get(reverse("core:healthz"))

    assert response.status_code == 200
    assert response.content == b"ok"
    assert "no-cache" in response.headers["Cache-Control"]


def test_healthz_rejects_post(client):
    assert client.post(reverse("core:healthz")).status_code == 405


def test_no_admin(client):
    assert client.get("/admin/").status_code == 404


def test_theme_switch_is_wired_up(client):
    html = _home(client)

    # The init script must load before the stylesheet to avoid a flash of the wrong theme.
    assert html.index("js/theme-init.js") < html.index("css/site.css")
    assert "data-theme-toggle" in html
    assert 'role="switch"' in html and 'aria-label="Dark theme"' in html
    assert '<meta name="color-scheme" content="light dark">' in html
