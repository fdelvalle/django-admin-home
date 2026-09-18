"""Optional "Pages" group: links to custom (non-model) routes in the navigation.

Each entry is a link to an already-existing project route (a dashboard, an
API doc page, a tool, ...). This module only *lists* those links in the
admin navigation — actual access to each page is still decided by its own
view (``is_staff`` / ``PermissionRequiredMixin`` / etc.), unchanged.

Configured via ``settings.ADMIN_HOME_CUSTOM_PAGES``, a list of dicts:

    key         stable item key (used by favorites/access counter).
                Prefixed ``page.`` so it never collides with a model key
                (``app_label.model``).
    name        label shown in the menu.
    icon        sprite symbol name (see admin_home/_icon_sprite.html).
    url_name    route ``name`` to resolve via ``reverse()``.
    url_args    (optional) positional args passed to ``reverse()``.
    permission  (optional) Django permission (``app_label.codename``)
                gating the link's *visibility*. Empty = visible to any
                staff user. A superuser always sees it.
    new_tab     (optional) open in a new browser tab.

No setting configured (or an empty list) means the group never appears.
"""

from __future__ import annotations

from django.conf import settings

CUSTOM_PAGES_GROUP_KEY = "app.pages"
CUSTOM_PAGES_GROUP_NAME = "Pages"
CUSTOM_PAGES_GROUP_ICON = "grid"

_DEFAULT_ICON = "list"


def _custom_pages() -> list[dict]:
    return getattr(settings, "ADMIN_HOME_CUSTOM_PAGES", None) or []


def _can_see_page(user, permission: str | None) -> bool:
    """Visibility rule for a page link.

    - Anonymous: never.
    - No permission required: any ``is_staff`` user.
    - Permission required: a superuser always sees it; otherwise
      ``user.has_perm(...)``.

    Never affects the page's real access — only whether the link shows up.
    """
    if not getattr(user, "is_authenticated", False):
        return False
    if not getattr(user, "is_staff", False):
        return False
    if not permission:
        return True
    if getattr(user, "is_superuser", False):
        return True
    try:
        return user.has_perm(permission)
    except Exception:
        return False


def build_custom_pages_group(user, favorites: set[str] | None = None) -> dict | None:
    """Builds the "Pages" group node with the links visible to ``user``.

    Returns ``None`` when no link is visible (so an empty group is never
    rendered), or when ``ADMIN_HOME_CUSTOM_PAGES`` is unset/empty. Resolves
    each URL defensively via ``reverse()``: a route that doesn't exist or
    resolve is simply skipped — the menu must never break.
    """
    from django.urls import NoReverseMatch, reverse

    pages = _custom_pages()
    if not pages:
        return None

    favorites = favorites or set()
    items = []
    for page in pages:
        if not _can_see_page(user, page.get("permission")):
            continue
        try:
            url = reverse(page["url_name"], args=page.get("url_args") or [])
        except NoReverseMatch:
            continue
        key = page["key"]
        items.append(
            {
                "key": key,
                "name": page["name"],
                "icon": page.get("icon", _DEFAULT_ICON),
                "url": url,
                "add_url": None,
                "new_tab": bool(page.get("new_tab")),
                "is_favorite": key in favorites,
            }
        )
    if not items:
        return None
    return {
        "key": CUSTOM_PAGES_GROUP_KEY,
        "name": CUSTOM_PAGES_GROUP_NAME,
        "icon": CUSTOM_PAGES_GROUP_ICON,
        "url": items[0]["url"],
        "models": items,
        "is_favorite": CUSTOM_PAGES_GROUP_KEY in favorites,
    }
