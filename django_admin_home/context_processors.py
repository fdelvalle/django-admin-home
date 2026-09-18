"""Template context for the admin's user menu (identity + language switcher).

Two independent context processors, both defensive (never raise, never
crash the admin) and both driven entirely by settings/Django itself — no
project-specific data:

- ``admin_user``: the current user's initials, for the header avatar.
- ``admin_languages``: the list of configured languages (from
  ``settings.LANGUAGES``), each with its native label and an icon name,
  for the language switcher. Labels/icons are optionally overridden via
  ``ADMIN_HOME_LANGUAGE_LABELS`` / ``ADMIN_HOME_LANGUAGE_FLAGS`` (dicts
  keyed by language code, e.g. ``"pt-br"``); a language missing from
  those dicts falls back to Django's own label and to the ``"globe"``
  sprite icon.
"""

from __future__ import annotations

import re

from django.conf import settings
from django.utils.translation import get_language

_FALLBACK_FLAG = "globe"


def _initials(user) -> str:
    """Up to two initials for the avatar. "?" when the user has no readable name."""
    source = (user.get_full_name() or "").strip() if hasattr(user, "get_full_name") else ""
    if not source:
        source = (getattr(user, "username", "") or "").strip()
    parts = [p for p in re.split(r"[ ,.\-_]+", source) if p]
    return "".join(p[0].upper() for p in parts[:2]) or "?"


def admin_user(request):
    """Exposes ``admin_home_user_initials`` for the logged-in user's avatar."""
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return {}
    return {"admin_home_user_initials": _initials(user)}


def admin_languages(request):
    """Exposes ``admin_home_languages``: code/label/icon/is_active per configured language.

    Built from ``settings.LANGUAGES`` — there is no separate list to keep in
    sync. Native labels/icons come from the optional settings above; a
    language without an entry there still works, just with Django's default
    label and a generic globe icon.
    """
    labels = getattr(settings, "ADMIN_HOME_LANGUAGE_LABELS", None) or {}
    flags = getattr(settings, "ADMIN_HOME_LANGUAGE_FLAGS", None) or {}
    current = (get_language() or settings.LANGUAGE_CODE or "").lower()

    languages = []
    for code, fallback_label in settings.LANGUAGES:
        key = code.lower()
        languages.append(
            {
                "code": code,
                "label": labels.get(key, str(fallback_label)),
                "icon": flags.get(key, _FALLBACK_FLAG),
                "is_active": key == current,
            }
        )
    return {"admin_home_languages": languages}
