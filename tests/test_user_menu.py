"""Tests for the header user menu: context processors + template rendering."""

from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory, TestCase, override_settings

from django_admin_home.context_processors import admin_languages, admin_user

OVERRIDE_TEMPLATES_DIR = str(Path(__file__).parent / "testapp" / "override_templates")


class AdminUserContextProcessorTests(TestCase):
    def test_anonymous_user_gets_no_context(self):
        request = RequestFactory().get("/admin/")
        request.user = AnonymousUser()
        self.assertEqual(admin_user(request), {})

    def test_initials_from_full_name(self):
        User = get_user_model()
        user = User(username="jsmith", first_name="Jane", last_name="Smith")
        request = RequestFactory().get("/admin/")
        request.user = user
        self.assertEqual(admin_user(request), {"admin_home_user_initials": "JS"})

    def test_initials_fall_back_to_username(self):
        User = get_user_model()
        user = User(username="root")
        request = RequestFactory().get("/admin/")
        request.user = user
        self.assertEqual(admin_user(request), {"admin_home_user_initials": "R"})


class AdminLanguagesContextProcessorTests(TestCase):
    def test_uses_django_label_and_globe_icon_when_unconfigured(self):
        request = RequestFactory().get("/admin/")
        languages = admin_languages(request)["admin_home_languages"]
        pt_br = next(lang for lang in languages if lang["code"] == "pt-br")
        self.assertEqual(pt_br["label"], "Portuguese (Brazil)")
        self.assertEqual(pt_br["icon"], "globe")

    @override_settings(
        ADMIN_HOME_LANGUAGE_LABELS={"pt-br": "Português (BR)"},
        ADMIN_HOME_LANGUAGE_FLAGS={"pt-br": "flag-br"},
    )
    def test_settings_override_label_and_icon(self):
        request = RequestFactory().get("/admin/")
        languages = admin_languages(request)["admin_home_languages"]
        pt_br = next(lang for lang in languages if lang["code"] == "pt-br")
        self.assertEqual(pt_br["label"], "Português (BR)")
        self.assertEqual(pt_br["icon"], "flag-br")

    def test_active_language_flagged(self):
        request = RequestFactory().get("/admin/")
        languages = admin_languages(request)["admin_home_languages"]
        active = [lang["code"] for lang in languages if lang["is_active"]]
        self.assertEqual(active, ["en"])  # settings.LANGUAGE_CODE


class UserMenuRenderTests(TestCase):
    """Full-stack check: the menu renders on a real admin page."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(username="root4", email="root4@example.com", password="x")
        self.client.force_login(self.user)

    def test_menu_renders_identity_languages_and_theme(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("admin-home-user-menu", html)
        self.assertIn("admin-home-user-menu__langs", html)
        self.assertIn('data-theme-value="dark"', html)
        self.assertIn(">R<", html)  # avatar initials for username "root4" (no separators to split on)

    def test_change_password_and_logout_links_present(self):
        response = self.client.get("/admin/")
        html = response.content.decode()
        self.assertIn('href="/admin/password_change/"', html)
        self.assertIn('action="/admin/logout/"', html)

    def test_extra_actions_extension_point_is_empty_by_default(self):
        response = self.client.get("/admin/")
        html = response.content.decode()
        self.assertNotIn("admin-home-user-menu__action--extra", html)

    def test_extra_actions_extension_point_is_overridable(self):
        templates = [dict(entry) for entry in settings.TEMPLATES]
        templates[0]["DIRS"] = [OVERRIDE_TEMPLATES_DIR]
        with override_settings(TEMPLATES=templates):
            response = self.client.get("/admin/")
        html = response.content.decode()
        self.assertIn("admin-home-user-menu__action--extra", html)
