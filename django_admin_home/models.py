from __future__ import annotations

from django.conf import settings
from django.db import models


class MenuFavorite(models.Model):
    """A menu item a user pinned as a favorite.

    ``menu_key`` references a stable navigation key (see
    :mod:`django_admin_home.menu`), e.g. ``app_label.model_name`` or
    ``app.<app_label>``. Not a ``ContentType`` FK: the navigation also
    includes non-model entries (custom pages, the "home" link).
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="admin_home_favorites")
    menu_key = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "menu_key")
        ordering = ["created_at"]
        verbose_name = "Menu favorite"
        verbose_name_plural = "Menu favorites"

    def __str__(self):
        return f"{self.user} → {self.menu_key}"


class MenuAccess(models.Model):
    """Per-user access counter for a menu item, powering the "most accessed" cards."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="admin_home_accesses")
    menu_key = models.CharField(max_length=255)
    access_count = models.PositiveIntegerField(default=0)
    last_access = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "menu_key")
        ordering = ["-access_count", "-last_access"]
        verbose_name = "Menu access"
        verbose_name_plural = "Menu accesses"

    def __str__(self):
        return f"{self.user} → {self.menu_key} ({self.access_count})"
