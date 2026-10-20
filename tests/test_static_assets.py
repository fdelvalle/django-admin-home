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

    def test_filter_chevron_overrides_django_arrow_glyph(self):
        # Django's changelists.css loads later and sets content: '→'/'↓' on the
        # same summary::before; the package rule must win in both states.
        css = (STATIC_DIR / "css" / "filter_panel.css").read_text()
        self.assertIn("#changelist #changelist-filter details > summary::before", css)
        self.assertIn("#changelist #changelist-filter details[open] > summary::before", css)

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


class PageLoadFlashTests(SimpleTestCase):
    """The sidebar/filter state must be in place before the first paint;
    otherwise every page load shows them open and animates them closed."""

    def test_preload_snippet_is_included_after_the_sidebar(self):
        sidebar = (PACKAGE_DIR / "templates" / "admin" / "nav_sidebar.html").read_text()
        self.assertGreater(sidebar.index('{% include "admin_home/_preload.html" %}'), sidebar.index("</nav>"))

    def test_preload_snippet_mirrors_the_storage_keys_of_the_deferred_scripts(self):
        snippet = (PACKAGE_DIR / "templates" / "admin_home" / "_preload.html").read_text()
        nav = (STATIC_DIR / "js" / "nav.js").read_text()
        filters = (STATIC_DIR / "js" / "filter_panel.js").read_text()
        for key in ("admin-home:nav-collapsed", "admin-home:nav-group:"):
            self.assertIn(key, nav)
            self.assertIn(key, snippet)
        self.assertIn("admin-home:filter-collapsed", filters)
        self.assertIn("admin-home:filter-collapsed", snippet)
        self.assertIn("(max-width: 767px)", nav)
        self.assertIn("(max-width: 767px)", snippet)

    def test_transitions_are_off_while_preloading(self):
        nav_css = (STATIC_DIR / "css" / "nav.css").read_text()
        filter_css = (STATIC_DIR / "css" / "filter_panel.css").read_text()
        self.assertIn("html.admin-home-preload *", nav_css)
        self.assertIn("html.admin-home-filter-precollapsed #changelist #changelist-filter", filter_css)

    def test_hscroll_coalesces_layout_work_into_one_frame(self):
        js = (STATIC_DIR / "js" / "hscroll.js").read_text()
        self.assertIn("requestAnimationFrame(refresh)", js)
        self.assertIn('addEventListener("scroll", schedule', js)
        self.assertNotIn('addEventListener("scroll", refresh', js)


class NoDataConcatenatedIntoHtmlTests(SimpleTestCase):
    def test_favorite_card_sets_key_and_icon_through_the_dom(self):
        js = (STATIC_DIR / "js" / "nav.js").read_text()
        self.assertNotIn("data-menu-key=\"' + meta.key", js)
        self.assertNotIn("onclick=", js)

    def test_filter_header_labels_use_text_content(self):
        js = (STATIC_DIR / "js" / "filter_panel.js").read_text()
        self.assertNotIn("+ filtersLabel +", js)
        self.assertNotIn("+ toggleLabel +", js)
