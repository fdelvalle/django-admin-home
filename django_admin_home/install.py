"""Installs the sidebar navigation + home dashboard on an ``AdminSite``."""

from __future__ import annotations

from django.conf import settings
from django.contrib import admin
from django.urls import path

from django_admin_home.menu import build_menu_tree, flatten_menu_items
from django_admin_home.pages import build_custom_pages_group
from django_admin_home.views import toggle_favorite, track_access


def _max_most_accessed() -> int:
    return getattr(settings, "ADMIN_HOME_MAX_MOST_ACCESSED", 8)


def _favorite_keys(user):
    from django_admin_home.models import MenuFavorite

    return set(MenuFavorite.objects.filter(user=user).values_list("menu_key", flat=True))


def _menu_tree_for_request(site, request):
    """Builds the menu tree honouring permissions (via ``get_app_list``)."""
    try:
        app_list = site.get_app_list(request)
    except Exception:
        app_list = []
    favorites = _favorite_keys(request.user) if request.user.is_authenticated else set()
    menu_tree = build_menu_tree(app_list, favorites=favorites)

    # Appends the "Pages" group (custom, non-model links), respecting
    # permissions. Additive and defensive: any failure here must never
    # prevent the rest of the menu from being built.
    try:
        pages_group = build_custom_pages_group(request.user, favorites=favorites)
        if pages_group:
            menu_tree = menu_tree + [pages_group]
    except Exception:
        pass

    return menu_tree, favorites


def _most_accessed(user, menu_index):
    """Top items accessed by the user that still exist in the navigation."""
    from django_admin_home.models import MenuAccess

    rows = (
        MenuAccess.objects.filter(user=user)
        .order_by("-access_count", "-last_access")
        .values("menu_key", "access_count")
    )
    cards = []
    max_items = _max_most_accessed()
    for row in rows:
        meta = menu_index.get(row["menu_key"])
        if not meta or not meta.get("url"):
            continue
        cards.append({**meta, "access_count": row["access_count"]})
        if len(cards) >= max_items:
            break
    return cards


def _favorites_cards(menu_index, favorites):
    cards = []
    for key in favorites:
        meta = menu_index.get(key)
        if meta and meta.get("url"):
            cards.append(meta)
    cards.sort(key=lambda c: (c["name"] or "").lower())
    return cards


def install(site: admin.AdminSite | None = None) -> None:
    """Applies the sidebar + home dashboard customization to ``site``.

    Idempotent (safe to call more than once) and additive: wraps
    ``each_context``/``index``/``get_urls``, preserving the originals, and
    never touches ``site_header``/``site_title``/``index_title`` or
    ``has_permission`` — those stay a project-level concern.

    Call this once, for example from your own app's ``AppConfig.ready()``::

        from django_admin_home import install

        class MyAppConfig(AppConfig):
            def ready(self):
                install()
    """
    site = site or admin.site

    if getattr(site, "_admin_home_installed", False):
        return

    original_each_context = site.each_context
    original_index = site.index
    original_get_urls = site.get_urls

    def each_context(request):
        context = original_each_context(request)
        try:
            menu_tree, favorites = _menu_tree_for_request(site, request)
            context["admin_home_menu_tree"] = menu_tree
            context["admin_home_menu_favorites"] = _favorites_cards(flatten_menu_items(menu_tree), favorites)
        except Exception:
            # The sidebar is additive; it must never break the admin.
            context.setdefault("admin_home_menu_tree", [])
            context.setdefault("admin_home_menu_favorites", [])
        return context

    def index(request, extra_context=None):
        extra_context = extra_context or {}
        try:
            menu_tree, favorites = _menu_tree_for_request(site, request)
            menu_index = flatten_menu_items(menu_tree)
            extra_context["admin_home_most_accessed"] = _most_accessed(request.user, menu_index)
            extra_context["admin_home_favorite_cards"] = _favorites_cards(menu_index, favorites)
        except Exception:
            extra_context.setdefault("admin_home_most_accessed", [])
            extra_context.setdefault("admin_home_favorite_cards", [])
        return original_index(request, extra_context)

    def get_urls():
        custom = [
            path(
                "menu/toggle-favorite/",
                site.admin_view(toggle_favorite),
                name="admin_home_toggle_favorite",
            ),
            path(
                "menu/track-access/",
                site.admin_view(track_access),
                name="admin_home_track_access",
            ),
        ]
        return custom + original_get_urls()

    site.each_context = each_context
    site.index = index
    site.get_urls = get_urls

    site._admin_home_installed = True
