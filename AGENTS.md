# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, Copilot, Cursor and others) working in this
repository. Human-facing docs are in [README.md](README.md).

## What this is

A Django 6 website for **Dishari** ("Dream of New Earth", established 2001), a nonprofit in
Noakhali, Bangladesh. It is a single-page site deployed on **Vercel** (serverless). It can also
run under gunicorn on any server.

It is deliberately small: one app (`core`), **no database, no admin, no auth/sessions**, no
front-end build step and no JS framework. All content is hard-coded in `core/content.py`.

## Commands

Always use the project virtualenv (`.venv/bin/...` or `source .venv/bin/activate`).

```bash
pip install -r requirements-dev.txt     # setup
python manage.py runserver              # dev server at :8000 (browser auto-reloads on save)
pytest                                  # tests (must pass)
ruff check . && ruff format --check .   # lint + format (must pass)
```

For layout/CSS changes, also run the responsive audit against the dev server. It needs a
Chrome/Chromium binary and should print "✓ no issues" for every width:

```bash
node tools/responsive_audit.mjs /path/to/chrome http://127.0.0.1:8000/ /tmp/shots
```

Exit codes: `0` all widths passed, `1` layout issues found, `2` usage error or the audit
couldn't run (for example, the dev server isn't running). Chrome is always shut down afterwards.

Before you finish a change, run `ruff format .`, `ruff check .` and `pytest`. CI runs the same
checks on Python 3.12–3.14, plus a lockfile check, `check --deploy` and `collectstatic` with
production settings.

## Git workflow

- **Never commit or push to `master`**: it is the live site. Work on a branch named
  `<type>/<issue-number>-<short-description>` and open a pull request. Only the maintainer
  (@msneloy) reviews and merges. Never merge your own pull request. The full contributor
  workflow is in README.md → *Contributing*.
- Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`,
  `test:`, `ci:`, `build:`, `chore:`, `refactor:`, `style:`, with `!` and a `BREAKING CHANGE:`
  footer for breaking changes. The subject is imperative and at most ~72 characters. The body
  explains what changed and why, in enough detail for the next developer.
- Keep commits logical and self-contained. Each one should pass the tests.

## Architecture map

| Path | Purpose |
| --- | --- |
| `core/content.py` | **All site copy**: `ORGANISATION` (contact details, mission, hero phrases), `SERVICE_AREAS`, `PROJECTS`, `TRAININGS`, as frozen dataclasses |
| `core/views.py` | `HomeView` (passes the content tuples to the template), `healthz` |
| `core/context_processors.py` | Injects `site` (= `ORGANISATION`) into every template |
| `core/templatetags/site_tags.py` | `{% icon "name" size %}` inline SVG icons |
| `config/settings/base.py` | Shared settings; env helpers `env`, `env_bool`, `env_list`; CSP |
| `config/settings/{dev,test,prod}.py` | Per-environment overrides. `prod.py` handles Vercel hosts and the proxy header |
| `templates/` | `base.html`, `partials/` (header, footer), `core/home.html`, `404.html`, `500.html` |
| `static/css/site.css` | All styles; design tokens in `:root` |
| `static/js/site.js` | Theme switch, mobile nav, header shadow, rotating hero phrase (progressive enhancement) |
| `static/js/theme-init.js` | Applies the saved theme before first paint (loaded in `<head>`) |
| `static/img/` | Logo, favicons, about photo, `training/` photos |
| `public/` | Served at `/` (`favicon.ico`, `robots.txt`): Vercel CDN, or WhiteNoise elsewhere |
| `pyproject.toml` / `uv.lock` | Dependency source of truth. `requirements*.txt` are generated from the lock |
| `tests/` | pytest suite (`test_content.py`, `test_views.py`, `test_settings.py`, `test_settings_dev.py`, `test_social_preview.py`) |
| `tools/responsive_audit.mjs` | Headless-Chrome layout audit across 10 widths (Node 22+, no deps) |
| `tools/theme_test.mjs` | Headless-Chrome test of the light/dark theme logic (Node 22+, no deps) |
| `tools/make_social_image.py` | Generates `static/img/social-preview.png`, the 1200×630 link-preview image (needs Pillow) |
| `.github/workflows/ci.yml` | CI: lock sync, ruff, pytest, deploy checks |

## Conventions and rules

- **Content changes go in `core/content.py`**, not in templates. Keep the dataclasses frozen
  and use tuples. Derived values (e.g. `phone_e164`, `whatsapp_url`) are properties, never
  duplicated strings.
- **Do not add a database, models, admin, auth or sessions** unless the user explicitly asks.
  When they do, the planned path is: models that mirror the dataclasses in `content.py`, a
  hosted Postgres DB (Vercel has no persistent disk, so no SQLite) and S3-compatible storage
  for any uploaded images.
- **Link previews** (Open Graph + Twitter tags) live in `templates/base.html`. All their URLs
  must be absolute: build them from `site_url` / `canonical_url` (context processor), which use
  `settings.SITE_URL` (`DJANGO_SITE_URL`) when set. The description is `ORGANISATION.summary`.
  The image is generated: change `tools/make_social_image.py` and re-run it. Don't hand-edit the
  PNG. Keep it 1200×630, opaque and under 300 KB; `tests/test_social_preview.py` enforces this.
- Images are static files in `static/img/`. Resize photos for the web (≤ 1200px wide, JPEG
  quality ~80) before committing.
- **No inline `<script>` and no third-party scripts, fonts or CDNs.** The Content Security Policy
  (`SECURE_CSP` in `base.py`) only allows `'self'`. Pass data to JS with `json_script`.
- **Light and dark themes.** Every colour in `site.css` is a semantic token defined once as a
  `light-dark(<light>, <dark>)` pair in `:root`. Never hard-code a colour in a component rule:
  add or reuse a token. `static/js/theme-init.js` must stay a tiny blocking script in `<head>`,
  before the stylesheet, so a saved theme applies before first paint. The choice is stored in
  `localStorage["theme"]`, and with no choice saved the site follows the OS setting.
  `theme-init.js` is the **single source of truth** for reading it: it exposes
  `window.dishariTheme` (`STORAGE_KEY`, `readSavedTheme()`, `systemTheme()`), and `site.js`
  must use that instead of reading `localStorage` itself. Only `"light"` and `"dark"` are valid.
  After changing theme logic, run `node tools/theme_test.mjs <chrome> http://127.0.0.1:8000/`.
  - The one exception to tokens is the day/night switch (`.theme-switch*`). Its sky, sun and moon
    are illustrative colours, so they're set with `:root[data-theme="dark"]` selectors. Its
    animations are enabled only after first paint, when `site.js` adds `.is-ready`.
- **Header controls share one height:** `--control-h` (40px) covers nav links, the "Contact us"
  CTA, the theme switch and the menu button. Use it for any new header control.
- **Hero phrases must fit on one line.** The title is sized in container query units (`cqi`)
  to fit the longest phrase, about 23 characters. If you change `hero_phrases`, run the
  responsive audit.
- Icons are inline SVGs from `site_tags.icon`. Add new ones to `_ICON_PATHS`.
- Keep the site usable without JS and accessible: semantic HTML, `alt` text, visible focus,
  `aria-*` on interactive controls, and support for `prefers-reduced-motion`.
- Brand: the logo green is `#078a35` (`--brand`). The logo is `static/img/logo.png`, the full
  mark plus wordmark with a transparent background. Don't recolour, crop or redraw it.
  `apple-touch-icon.png` stays on a white background on purpose, because iOS renders
  transparency as black.
- Design decisions the owner made. **Don't revert them:**
  - No team or staff section.
  - No photo or wallpaper behind the hero. It uses a light background with the full logo on the right.
  - A single header bar. There is no separate top bar for contact details, which belong in the
    Contact section.
  - A slim one-row footer.
  - The theme switch is the day/night style (sun with clouds, moon with stars), placed before
    "About" in the nav.
  - Contact cards are fully tappable (a stretched `a::after`). Keep tap targets at least 24px.
- Secrets come only from environment variables. Never commit `.env` or keys.
- Dependencies: edit `pyproject.toml`, then run `uv lock` and re-export the requirements files
  (commands in README). Never hand-edit `requirements*.txt` or `uv.lock`. CI checks they match.
- Python style: ruff (line length 100), type hints on new functions, small focused views.
- Add or update tests in `tests/` for every behaviour change.

## Gotchas

- Production uses `CompressedManifestStaticFilesStorage`. A `{% static %}` path that doesn't
  exist raises an error in prod. `tests/test_content.py` checks that every training image
  exists.
- On Vercel, `manage.py` defaults to prod settings (it checks the `VERCEL` env var).
  `wsgi.py` and `asgi.py` always default to prod.
- `django-browser-reload` is a **dev-only** dependency, enabled in `config/settings/dev.py` and
  `/__reload__/` is routed only when it is installed. Never add it to base or prod settings.
- In dev, `whitenoise.runserver_nostatic` makes WhiteNoise (not runserver) serve static files,
  with `WHITENOISE_MAX_AGE = 0`, so browsers never show a stale cached image or stylesheet.
  If an asset looks stale anyway, hard-refresh. Production uses hashed filenames, so this
  can't happen there.
- The page uses `scroll-behavior: smooth`. In browser automation, call
  `scrollIntoView({ behavior: "instant" })` before measuring positions.
- `500.html` is rendered without a request context, so keep it free of context variables.
- Supported Python on Vercel: 3.12 to 3.14 (pinned to 3.13 in `.python-version`). Don't use
  newer language features.
