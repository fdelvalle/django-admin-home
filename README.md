# django-admin-home

A tree-navigation sidebar, home dashboard and header user menu for the
Django admin.

By default, the Django admin's home page is a flat, alphabetical list of
every app/model the current user can access, and the built-in sidebar has
no favorites or usage-based shortcuts. This package replaces both with:

## Features

- A collapsible sidebar, grouped by app, built from the admin's own
  `get_app_list` — so it always respects the current user's permissions.
- A "Favorites" section and a star to pin/unpin any app or model
  (persisted per user).
- A home page with cards for favorites, most-accessed items (tracked per
  user), and every module, in a responsive grid (with an optional compact
  "masonry" layout).
- An optional "Pages" group for custom, non-model links (dashboards, API
  docs, external tools, ...), entirely configured via settings.
- A header user menu: identity, a language switcher (driven by
  `settings.LANGUAGES`), an explicit Auto/Light/Dark theme switcher, and
  account shortcuts (change password, log out).
- A dependency-free, offline SVG icon set (no external font/CDN).
- Defensive by design: any unexpected failure falls back to the native
  admin behaviour instead of breaking the page.

## Installation

```bash
pip install django-admin-home
```

Add it to `INSTALLED_APPS` (it ships models, so run `migrate` afterwards):

```python
INSTALLED_APPS = [
    "django_admin_home",
    ...
    "django.contrib.admin",
]
```

Enable it, once — e.g. in your own app's `AppConfig.ready()`:

```python
from django.apps import AppConfig


class MyAppConfig(AppConfig):
    def ready(self):
        from django_admin_home import install

        install()
```

Include the bundled CSS/JS in your `admin/base_site.html`:

```django
{% load static %}
<link rel="stylesheet" href="{% static 'django_admin_home/css/nav.css' %}">
<link rel="stylesheet" href="{% static 'django_admin_home/css/home.css' %}">
<link rel="stylesheet" href="{% static 'django_admin_home/css/user_menu.css' %}">
<script src="{% static 'django_admin_home/js/nav.js' %}" defer></script>
<script src="{% static 'django_admin_home/js/user_menu.js' %}" defer></script>
```

Run migrations:

```bash
python manage.py migrate django_admin_home
```

### Header user menu (optional)

The user menu (identity, language switcher, theme switcher, account
shortcuts) needs two context processors and a template include:

```python
TEMPLATES = [{
    ...,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        ...,
        "django_admin_home.context_processors.admin_user",
        "django_admin_home.context_processors.admin_languages",
    ]},
}]
```

```django
{% block usertools %}
    {% if has_permission %}
        <div id="user-tools">{% include "admin_home/_user_menu.html" %}</div>
    {% endif %}
{% endblock %}
```

The language switcher lists whatever is in `settings.LANGUAGES` and posts
to Django's own `set_language` view — make sure
`django.middleware.locale.LocaleMiddleware` and `django.contrib.admin`'s
`i18n` URLs are enabled. The theme switcher reuses the Django admin's own
`localStorage.theme` + `data-theme` contract, so it stays in sync with the
native toggle (which this menu hides, in favour of the explicit picker).

To add project-specific links to the menu (e.g. an internal tool), override
the template `admin_home/_user_menu_extra_actions.html` (empty by default).

## Settings (all optional)

```python
# Icon per app/model. Value is a symbol name from the bundled SVG sprite
# (admin_home/_icon_sprite.html) — add your own <symbol> there via a
# template override if you need more icons.
ADMIN_HOME_APP_ICONS = {"buyers": "building", "cards": "card"}
ADMIN_HOME_MODEL_ICONS = {"buyers.buyer": "building"}

# Extra, non-model links shown in a "Pages" group.
ADMIN_HOME_CUSTOM_PAGES = [
    {
        "key": "page.dashboard",
        "name": "Dashboard",
        "icon": "gauge",
        "url_name": "dashboard_index",
        "permission": "account.view_menu_dashboard",  # optional
        "new_tab": True,
    },
]

# How many "most accessed" cards to show on the home page (default 8).
ADMIN_HOME_MAX_MOST_ACCESSED = 8

# Native label / sprite icon per language code, for the user menu's
# language switcher. A language missing here still works, with Django's
# own label and the bundled "globe" icon. The package ships no flag
# icons — any name in ADMIN_HOME_LANGUAGE_FLAGS must exist in the sprite,
# which means adding your own <symbol> via a template override of
# admin_home/_icon_sprite.html (see "Overriding the brand/logo" below).
ADMIN_HOME_LANGUAGE_LABELS = {"pt-br": "Português (BR)", "es": "Español"}
ADMIN_HOME_LANGUAGE_FLAGS = {"pt-br": "flag-br", "es": "flag-es"}
```

## Overriding the brand/logo

The sidebar header includes `admin_home/_brand.html`, which by default just
shows `site_header` as text. To show your own logo, place a template at
the same path earlier in your project's template resolution (e.g.
`templates/admin_home/_brand.html` in your project, with `APP_DIRS` search
order putting your project templates before installed apps).

## What this package intentionally does not do

- It does not set `site_header` / `site_title` / `index_title` — that
  stays a project-level decision.
- It does not touch `AdminSite.has_permission` — any extra access rules
  are the host project's responsibility.
- It does not migrate data from a previous, project-specific
  favorites/access-tracking implementation.
- It does not ship any country flag icons, or a Rosetta/translation-tool
  link — both are left to the host project via settings/template
  overrides (see above).
