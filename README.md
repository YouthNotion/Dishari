# Dishari: Dream of New Earth

The website for **Dishari** (established 2001), a nonprofit, nonpolitical organisation in
Noakhali, Bangladesh. Dishari provides shelter, education, healthcare, legal aid and training
for abandoned children, vulnerable women and elderly women.

Built with **Django 6**. It is deliberately small:

- **No database or admin yet.** All content lives in [`core/content.py`](core/content.py).
- **No front-end framework or build step.** One stylesheet and two small vanilla JS files.
- **Light and dark themes.** It follows the visitor's OS setting, and a day/night switch in the
  header overrides it.
- **Responsive and accessible.** Audited at 320–1440px, it works without JavaScript and meets
  the WCAG 2.2 tap-target size.
- **Secure by default.** A strict Content-Security-Policy, HTTPS and HSTS in production, and
  no third-party requests.

## Quick start

Requires Python 3.12 or newer.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python manage.py runserver
```

Open <http://127.0.0.1:8000>. The dev server restarts on Python changes, and the open browser tab
reloads itself whenever you save a template, CSS, JS or Python file
([django-browser-reload](https://github.com/adamchainz/django-browser-reload), dev only).

## Editing content

| To change… | Edit |
| --- | --- |
| Phone, WhatsApp, email, address, Facebook, mission text, hero phrases | `ORGANISATION` in `core/content.py` |
| Services, projects, training programmes | `SERVICE_AREAS`, `PROJECTS`, `TRAININGS` in `core/content.py` |
| Training photos | add the image to `static/img/training/` (≤ 1200px wide, JPEG ~80%) and point `image=` at it |
| Page layout | `templates/` |
| Styles and colours | `static/css/site.css` (light/dark colour tokens are at the top) |

Notes:

- The WhatsApp link and the `tel:` link are generated from the phone number.
- "Years of service" in the hero is calculated from `established_year` automatically.
- Hero phrases must fit on one line. Keep each one to about 23 characters (the current longest,
  "shelter for the elderly", is 23) and run the responsive audit after changing them.

## Development

| Task | Command |
| --- | --- |
| Run the dev server | `python manage.py runserver` |
| Run tests | `pytest` |
| Lint / format | `ruff check .` / `ruff format .` |
| Responsive audit (needs Chrome/Chromium) | `node tools/responsive_audit.mjs <chrome> http://127.0.0.1:8000/ <shots-dir>` |
| Add or upgrade a dependency | edit `pyproject.toml`, then `uv lock` and re-export (below) |

Dependencies are declared in `pyproject.toml` and locked in `uv.lock`. The `requirements*.txt`
files are generated from the lock. Don't edit them by hand:

```bash
uv lock
uv export --format requirements-txt --no-dev --no-hashes --no-emit-project -o requirements.txt
uv export --format requirements-txt --extra dev --no-hashes --no-emit-project -o requirements-dev.txt
```

The responsive audit loads the site in headless Chrome at 10 widths. It checks for sideways
overflow, tap targets under 24px, the smallest font size, that the hero phrases fit, and that
the mobile menu works. Run it after layout or CSS changes. It uses only Node 22+ built-ins.

### Workflow

- Branch from `master`, open a pull request, and let CI pass before merging.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `docs:`, `test:`, `ci:`, `build:`, `chore:`). The body explains *what* and
  *why*.
- CI (`.github/workflows/ci.yml`) runs on Python 3.12–3.14. It checks that the lockfile and
  requirements are in sync, runs ruff and the tests, then runs `check --deploy` and
  `collectstatic` with production settings.

## Project layout

```text
config/                Django project
  settings/            base.py (shared), dev.py, test.py, prod.py (incl. Vercel handling)
  urls.py, wsgi.py, asgi.py
core/                  The website app
  content.py           ALL site copy and contact details (frozen dataclasses)
  views.py             Home page and /healthz
  context_processors.py  exposes the organisation as `site` in templates
  templatetags/        {% icon %} inline SVG icons
templates/             base.html, partials/ (header, footer), core/home.html, 404.html, 500.html
static/
  css/site.css         all styles; light/dark tokens at the top
  js/theme-init.js     applies a saved theme before first paint (loaded in <head>)
  js/site.js           theme switch, mobile menu, header shadow, rotating hero phrase
  img/                 logo (transparent), favicons, about photo, training/ photos
public/                served at the site root: favicon.ico, robots.txt
tests/                 pytest suite
tools/                 responsive_audit.mjs
.github/workflows/     CI
AGENTS.md              instructions for AI coding agents (CLAUDE.md points to it)
```

## Configuration

Settings are read from environment variables. See [`.env.example`](.env.example).

| Variable | Default | Notes |
| --- | --- | --- |
| `DJANGO_SETTINGS_MODULE` | `config.settings.dev` locally; `config.settings.prod` on Vercel and in wsgi/asgi | |
| `DJANGO_SECRET_KEY` | none | **Required** in production |
| `DJANGO_ALLOWED_HOSTS` | none | Comma-separated. `*.vercel.app` hosts are added automatically on Vercel |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | none | e.g. `https://example.org` |
| `DJANGO_SECURE_SSL_REDIRECT` | `true` | |
| `DJANGO_SECURE_HSTS_SECONDS` | `3600` | Raise (e.g. to `31536000`) once HTTPS is confirmed working |
| `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` | `false` | Only if every subdomain is HTTPS |
| `DJANGO_SECURE_HSTS_PRELOAD` | `false` | Only if you will submit the domain to the preload list |
| `DJANGO_BEHIND_TLS_PROXY` | `false` | Trust `X-Forwarded-Proto` (automatic on Vercel) |
| `DJANGO_LOG_LEVEL` | `INFO` | Root log level (logs go to stdout) |

## Deploying to Vercel

The site has no database and no uploads, so it runs on Vercel with no extra services.

1. Import the GitHub repository in Vercel. It detects Django from `manage.py`, installs
   dependencies from `pyproject.toml` + `uv.lock`, uses Python 3.13 (`.python-version`), runs
   `collectstatic` and serves `/static/` and `public/` from its CDN.
2. In **Project → Settings → Environment Variables**, set `DJANGO_SECRET_KEY` to a long random
   string. Generate one with
   `python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"`.
3. If you add a custom domain, also set `DJANGO_ALLOWED_HOSTS` and
   `DJANGO_CSRF_TRUSTED_ORIGINS` for it.

Make sure Vercel's **System Environment Variables** are exposed to the project (an option in the
same settings page). The settings use `VERCEL`, `VERCEL_URL` and
`VERCEL_PROJECT_PRODUCTION_URL` to allow the `*.vercel.app` hosts.

## Deploying to a server (gunicorn)

```bash
export DJANGO_SETTINGS_MODULE=config.settings.prod DJANGO_SECRET_KEY=... DJANGO_ALLOWED_HOSTS=...
pip install -r requirements.txt
python manage.py collectstatic --noinput
gunicorn config.wsgi --bind 0.0.0.0:8000
```

Static files are served by WhiteNoise (hashed and compressed, so browsers can cache them
forever). `GET /healthz` returns `ok` for uptime checks and is exempt from the HTTPS redirect.

## Roadmap

- Move `core/content.py` into database models with a Django admin so non-developers can edit
  content. The dataclasses in `content.py` already have the right shape for this. On Vercel this
  needs a hosted Postgres database and S3-compatible storage for uploaded images, because
  serverless functions have no persistent disk.
