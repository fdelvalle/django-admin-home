"""A tree-navigation sidebar + favorites/most-accessed home dashboard for the Django admin.

By default, the Django admin's home page is a flat, alphabetical list of
every app/model the user can access, and the built-in sidebar has no
favorites or usage-based shortcuts. This package replaces both with:

- A collapsible sidebar, grouped by app, with a "Favorites" section and a
  star to pin/unpin any item (persisted per user).
- A home page with cards for favorites, most-accessed items (tracked per
  user), and every module, in a responsive grid (with an optional compact
  "masonry" layout).
- An optional "Pages" group for custom, non-model links (dashboards, API
  docs, ...), configured entirely via settings.
- A dependency-free SVG icon set, offline (no external font/CDN).

Installation
------------
1. ``pip install django-admin-home``

2. Add ``"django_admin_home"`` to ``INSTALLED_APPS`` (it ships models, so
   run ``migrate`` afterwards)::

    INSTALLED_APPS = [
        "django_admin_home",
        ...
        "django.contrib.admin",
    ]

3. Enable it, once — e.g. in your own app's ``AppConfig.ready()``::

    from django_admin_home import install

    class MyAppConfig(AppConfig):
        def ready(self):
            install()

4. Include the bundled CSS/JS in your ``admin/base_site.html``::

    {% load static %}
    <link rel="stylesheet" href="{% static 'django_admin_home/css/nav.css' %}">
    <link rel="stylesheet" href="{% static 'django_admin_home/css/home.css' %}">
    <script src="{% static 'django_admin_home/js/nav.js' %}" defer></script>

Optional settings
------------------
- ``ADMIN_HOME_APP_ICONS`` / ``ADMIN_HOME_MODEL_ICONS``: dicts mapping an
  ``app_label`` (or ``app_label.model_name``) to an icon symbol name.
- ``ADMIN_HOME_CUSTOM_PAGES``: list of dicts describing extra, non-model
  links shown in a "Pages" group. See :mod:`django_admin_home.pages`.
- ``ADMIN_HOME_MAX_MOST_ACCESSED``: how many "most accessed" cards to show
  on the home page (default 8).
"""

from __future__ import annotations

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_APP_ICON",
    "DEFAULT_MODEL_ICON",
    "HOME_ICON",
    "MenuAccess",
    "MenuFavorite",
    "app_menu_key",
    "build_custom_pages_group",
    "build_menu_tree",
    "flatten_menu_items",
    "icon_for_app",
    "icon_for_model",
    "install",
    "model_menu_key",
]

# Names are resolved lazily (PEP 562) instead of imported eagerly here.
# Django imports this top-level package during app-registry population
# (phase 1, before any app's `models` module may be imported) just to
# discover this app's AppConfig — an eager `from .models import ...` (or
# anything that transitively imports models, like `install`/`views`) at
# that point raises AppRegistryNotReady.
_LAZY_ATTRS = {
    "install": "django_admin_home.install",
    "MenuAccess": "django_admin_home.models",
    "MenuFavorite": "django_admin_home.models",
    "build_custom_pages_group": "django_admin_home.pages",
    "DEFAULT_APP_ICON": "django_admin_home.menu",
    "DEFAULT_MODEL_ICON": "django_admin_home.menu",
    "HOME_ICON": "django_admin_home.menu",
    "app_menu_key": "django_admin_home.menu",
    "build_menu_tree": "django_admin_home.menu",
    "flatten_menu_items": "django_admin_home.menu",
    "icon_for_app": "django_admin_home.menu",
    "icon_for_model": "django_admin_home.menu",
    "model_menu_key": "django_admin_home.menu",
}


def __getattr__(name: str):
    module_path = _LAZY_ATTRS.get(name)
    if module_path is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    import importlib

    module = importlib.import_module(module_path)
    value = getattr(module, name)
    globals()[name] = value  # cache: subsequent access skips __getattr__
    return value
