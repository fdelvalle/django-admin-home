"""Builds the navigable menu tree from the admin's own ``app_list``.

The tree is derived from ``AdminSite.get_app_list(request)``, which already
respects the current user's permissions — this module only enriches each
app/model with an icon and a stable key, it never decides visibility.

Icons are referenced by *name* (a ``<symbol id="i-<name}">`` in the bundled
SVG sprite, see ``admin_home/_icon_sprite.html``), not by external font/CDN
classes, so the navigation keeps working offline. Any app/model without a
specific mapping falls back to a generic icon, so navigation keeps working
as new apps/models are added.

The "stable key" of each item (``menu_key``) is used both for favorites and
for the access counter:

    - Model item:  ``<app_label>.<object_name_lower>``  e.g. ``auth.user``
    - App group:   ``app.<app_label>``                  e.g. ``app.auth``
    - Home:        ``home``
"""

from __future__ import annotations

from django.conf import settings

DEFAULT_APP_ICON = "folder"
DEFAULT_MODEL_ICON = "list"
HOME_ICON = "home"

# Minimal built-in fallback so a stock Django project (auth app) already
# gets sensible icons. Projects override/extend via ADMIN_HOME_APP_ICONS /
# ADMIN_HOME_MODEL_ICONS.
_BUILTIN_APP_ICONS = {"auth": "shield"}
_BUILTIN_MODEL_ICONS = {"auth.user": "user", "auth.group": "users"}


def _app_icons() -> dict:
    icons = dict(_BUILTIN_APP_ICONS)
    icons.update(getattr(settings, "ADMIN_HOME_APP_ICONS", None) or {})
    return icons


def _model_icons() -> dict:
    icons = dict(_BUILTIN_MODEL_ICONS)
    icons.update(getattr(settings, "ADMIN_HOME_MODEL_ICONS", None) or {})
    return icons


def model_menu_key(app_label: str, object_name: str) -> str:
    """Stable key for a model item."""
    return f"{app_label}.{object_name}".lower()


def app_menu_key(app_label: str) -> str:
    return f"app.{app_label}".lower()


def icon_for_app(app_label: str) -> str:
    return _app_icons().get((app_label or "").lower(), DEFAULT_APP_ICON)


def icon_for_model(app_label: str, object_name: str) -> str:
    return _model_icons().get(model_menu_key(app_label, object_name), DEFAULT_MODEL_ICON)


def build_menu_tree(app_list, favorites: set[str] | None = None) -> list[dict]:
    """Turns the admin's ``app_list`` into a navigable tree.

    Each app node: ``{key, name, icon, url, models: [...], is_favorite}``.
    Each model node: ``{key, name, icon, url, add_url, is_favorite}``.

    ``favorites`` is the set of ``menu_key`` the current user favorited.
    """
    favorites = favorites or set()
    tree = []
    for app in app_list:
        app_label = app.get("app_label") or ""
        app_key = app_menu_key(app_label)
        models = []
        for model in app.get("models", []):
            object_name = (model.get("object_name") or model.get("name") or "").strip()
            key = model_menu_key(app_label, object_name)
            models.append(
                {
                    "key": key,
                    "name": model.get("name"),
                    "icon": icon_for_model(app_label, object_name),
                    "url": model.get("admin_url"),
                    "add_url": model.get("add_url"),
                    "is_favorite": key in favorites,
                }
            )
        tree.append(
            {
                "key": app_key,
                "name": app.get("name"),
                "icon": icon_for_app(app_label),
                "url": app.get("app_url"),
                "models": models,
                "is_favorite": app_key in favorites,
            }
        )
    return tree


def flatten_menu_items(menu_tree) -> dict:
    """Index ``menu_key -> metadata`` (apps + models).

    Used to resolve "most accessed" and "favorites" cards from the
    persisted keys, keeping name/icon/url in sync with the live menu.
    """
    index: dict = {}
    for app in menu_tree:
        index[app["key"]] = {
            "key": app["key"],
            "name": app["name"],
            "icon": app["icon"],
            "url": app["url"],
            "parent": None,
        }
        for model in app["models"]:
            index[model["key"]] = {
                "key": model["key"],
                "name": model["name"],
                "icon": model["icon"],
                "url": model["url"],
                "parent": app["name"],
                "new_tab": bool(model.get("new_tab")),
            }
    return index
