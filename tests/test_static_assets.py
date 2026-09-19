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

    def test_filter_facets_default_closed_and_remember_state(self):
        js = (STATIC_DIR / "js" / "filter_panel.js").read_text()
        self.assertIn("data-filter-title", js)
        self.assertIn('addEventListener("toggle"', js)

    def test_mobile_sidebar_starts_collapsed_and_reserves_content_space(self):
        css = (STATIC_DIR / "css" / "nav.css").read_text()
        js = (STATIC_DIR / "js" / "nav.js").read_text()
        self.assertIn("MOBILE_BREAKPOINT", js)
        self.assertIn("media.matches ||", js)
        self.assertIn("flex: 0 0 var(--admin-home-nav-width-collapsed)", css)
        self.assertIn("padding-left: calc(16px + var(--admin-home-nav-width-collapsed))", css)

    def test_mobile_user_menu_is_kept_right_aligned_and_avatar_only(self):
        css = (STATIC_DIR / "css" / "user_menu.css").read_text()
        self.assertIn("flex-wrap: nowrap", css)
        self.assertIn("margin-left: auto", css)
        self.assertIn(".admin-home-user-menu__chevron", css)
        self.assertIn("flex-direction: row", css)

    def test_user_menu_panel_is_not_clipped_by_the_django_header(self):
        css = (STATIC_DIR / "css" / "user_menu.css").read_text()
        self.assertIn("overflow: visible", css)
        self.assertIn("z-index: 101", css)
        self.assertIn("#user-tools .admin-home-user-menu", css)
