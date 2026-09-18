"""Packaging sanity checks for the settings-free static extras (filter panel,
floating horizontal scrollbar): the files exist, are non-empty, and the
class names/icon referenced by the JS actually exist in the matching CSS
and in the bundled icon sprite."""

from pathlib import Path

from django.test import SimpleTestCase

import django_admin_home

PACKAGE_DIR = Path(django_admin_home.__file__).parent
STATIC_DIR = PACKAGE_DIR / "static" / "django_admin_home"
SPRITE_PATH = PACKAGE_DIR / "templates" / "admin_home" / "_icon_sprite.html"


class StaticAssetsExistTests(SimpleTestCase):
    def test_filter_panel_files_exist(self):
        css = (STATIC_DIR / "css" / "filter_panel.css").read_text()
        js = (STATIC_DIR / "js" / "filter_panel.js").read_text()
        self.assertIn(".admin-home-filter-header", css)
        self.assertIn("admin-home-filter-header", js)

    def test_hscroll_files_exist(self):
        css = (STATIC_DIR / "css" / "hscroll.css").read_text()
        js = (STATIC_DIR / "js" / "hscroll.js").read_text()
        self.assertIn(".admin-home-hscroll", css)
        self.assertIn("admin-home-hscroll", js)

    def test_filter_icon_is_in_the_sprite(self):
        sprite = SPRITE_PATH.read_text()
        self.assertIn('id="i-filter"', sprite)
        self.assertIn('id="i-chevron"', sprite)
