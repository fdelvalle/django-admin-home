from __future__ import annotations

from django.apps import AppConfig


class AdminHomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_admin_home"
    label = "admin_home"
    verbose_name = "Admin Home Dashboard"
