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

## Contributing (new developers, start here)

Thanks for helping! Whether you want to fix a bug, add something new or pick up an open
[issue](https://github.com/YouthNotion/Dishari/issues), the process is the same:
**work on a branch, open a pull request, and the maintainer reviews and merges it.**

> [!CAUTION]
> **Never push to `master`.** `master` is what runs the live website, so a single unreviewed
> bug pushed there can take the site down. All changes reach `master`
> only through a reviewed pull request, merged by the maintainer
> ([@msneloy](https://github.com/msneloy)).

### Step by step

1. **Pick something to work on.**
   - Browse the [open issues](https://github.com/YouthNotion/Dishari/issues). If you're new, start
     with [`good first issue`](https://github.com/YouthNotion/Dishari/labels/good%20first%20issue).
   - Comment on the issue so it can be assigned to you, and nobody else works on it at the same
     time.
   - Want to add something that has no issue yet? Open an issue first and describe the idea,
     so it can be agreed on before you spend time on it.

2. **Get the latest `master` and create a branch.**

   ```bash
   git switch master
   git pull
   git switch -c fix/3-healthz-head     # <type>/<issue-number>-<short-description>
   ```

   Branch name prefixes: `feat/` (new feature), `fix/` (bug fix), `docs/`, `test/`, `chore/`,
   `refactor/`.

3. **Make your change and run the checks locally.** Set up the project with the
   [Quick start](#quick-start) first.

   ```bash
   ruff format . && ruff check .   # formatting and lint
   pytest                          # tests
   ```

   - Add or update tests for any behaviour you change.
   - If you changed layout or CSS, also run the responsive audit (see [Development](#development)).
   - Check your change in both the light and the dark theme.

4. **Commit using [Conventional Commits](https://www.conventionalcommits.org/).**

   ```bash
   git commit -m "fix: allow HEAD requests on /healthz" -m "Uptime monitors probe with HEAD; require_GET rejected them with 405. Fixes #3."
   ```

   - Types: `feat:`, `fix:`, `docs:`, `test:`, `ci:`, `build:`, `chore:`, `refactor:`, `style:`.
   - The subject line is short and imperative. The body explains *what* changed and *why*.
   - Write `Fixes #<issue>` so the issue closes automatically when the pull request is merged.

5. **Push your branch and open a pull request into `master`.**

   ```bash
   git push -u origin fix/3-healthz-head
   ```

   Then open the pull request on GitHub, or run `gh pr create`. In the description, say:
   - **what** changed and **why** (link the issue)
   - **how you tested** it
   - **screenshots** (light and dark) for anything visual

6. **Wait for CI and review.**
   - CI must pass. It runs lint, tests and production checks on every pull request.
   - The maintainer reviews the code. If changes are requested, push more commits to the **same
     branch**, and the pull request updates itself.
   - **Only the maintainer merges.** Please don't merge your own pull request.

7. **After the merge**, clean up and start fresh for your next change:

   ```bash
   git switch master && git pull
   git branch -d fix/3-healthz-head
   ```

### Ground rules

- **Never push or force-push to `master`.** Don't force-push branches other people are working
  on either.
- **One topic per pull request.** Small pull requests get reviewed and merged faster.
- **Never commit secrets** (`.env`, keys, passwords). Configuration comes from environment
  variables, see [Configuration](#configuration).
- Follow the project conventions in [AGENTS.md](AGENTS.md). They apply to people as well as AI
  tools.
- Stuck or unsure? Ask in the issue or the pull request. Questions are welcome.

## Editing content

| To change… | Edit |
| --- | --- |
| Phone, WhatsApp, email, address, Facebook, mission text, hero phrases | `ORGANISATION` in `core/content.py` |
| Text shown in link previews and search results | `ORGANISATION.summary` in `core/content.py` (about 150 characters) |
| The link-preview image (WhatsApp, Messenger, Facebook…) | edit the wording in `tools/make_social_image.py`, then run `python tools/make_social_image.py` (needs `pip install pillow`) |
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

### Continuous integration

CI (`.github/workflows/ci.yml`) runs on every pull request, on Python 3.12–3.14. It checks that
the lockfile and requirements are in sync, runs ruff and the tests, then runs `check --deploy`
and `collectstatic` with production settings. Pull requests are only merged once CI passes.
For the branch and pull request workflow, see [Contributing](#contributing-new-developers-start-here).

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
tools/                 responsive_audit.mjs, theme_test.mjs, make_social_image.py
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
| `DJANGO_SITE_URL` | requested host | Canonical address, e.g. `https://dishari.orgs.bd`. Link previews and the canonical link always point here, even when shared from a `*.vercel.app` URL |
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
   `DJANGO_CSRF_TRUSTED_ORIGINS` for it, and set `DJANGO_SITE_URL` (e.g. `https://dishari.orgs.bd`)
   so link previews use the domain.

Make sure Vercel's **System Environment Variables** are exposed to the project (an option in the
same settings page). The settings use `VERCEL`, `VERCEL_URL` and
`VERCEL_PROJECT_PRODUCTION_URL` to allow the `*.vercel.app` hosts.

### Link previews

When the site is shared on WhatsApp, Messenger, Facebook, LinkedIn or X, the preview comes
from the Open Graph and Twitter tags in `templates/base.html`: the title, `ORGANISATION.summary`,
and `static/img/social-preview.png` (1200×630, under 300 KB). Apps cache previews, so after
changing them, refresh Facebook and Messenger with the
[Sharing Debugger](https://developers.facebook.com/tools/debug/) ("Scrape Again"). WhatsApp keeps
its own cache and updates on its own after a while; to test immediately, share the link with
a harmless query string such as `https://dishari.orgs.bd/?v=2`.

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
