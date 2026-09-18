"""Regression test: every name in __all__ must be importable from the top-level package."""

from django.test import SimpleTestCase

import django_admin_home


class PublicApiTests(SimpleTestCase):
    def test_top_level_exports(self):
        for name in django_admin_home.__all__:
            self.assertTrue(hasattr(django_admin_home, name), f"{name!r} is in __all__ but missing from the package")
