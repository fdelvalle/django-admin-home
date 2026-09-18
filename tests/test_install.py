"""Integration tests for django_admin_home.install.

``install()`` is already applied to the default admin.site by
tests/conftest.py (module import time), so these tests exercise the
resulting behaviour rather than calling install() themselves.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from django_admin_home import install
from django_admin_home.models import MenuAccess, MenuFavorite


class InstallIdempotencyTests(TestCase):
    def test_second_call_is_a_no_op(self):
        patched_get_urls = admin.site.get_urls
        patched_index = admin.site.index
        install(admin.site)
        self.assertIs(admin.site.get_urls, patched_get_urls)
        self.assertIs(admin.site.index, patched_index)


class EachContextTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(username="root1", email="root1@example.com", password="x")

    def test_context_has_menu_tree_and_favorites_keys(self):
        request = RequestFactory().get("/admin/")
        request.user = self.user
        context = admin.site.each_context(request)
        self.assertIn("admin_home_menu_tree", context)
        self.assertIn("admin_home_menu_favorites", context)
        self.assertTrue(any(app["key"] == "app.testapp" for app in context["admin_home_menu_tree"]))


class IndexViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(username="root2", email="root2@example.com", password="x")
        self.client.force_login(self.user)

    def test_most_accessed_and_favorites_rendered(self):
        MenuFavorite.objects.create(user=self.user, menu_key="app.testapp")
        MenuAccess.objects.create(user=self.user, menu_key="app.testapp", access_count=3)

        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("admin-home-wrap", html)
        self.assertIn("admin-home-favorites-section", html)
        self.assertIn(">3<", html)  # access_count badge

    def test_empty_state_when_no_access_history(self):
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("admin-home-empty", response.content.decode())


class SidebarRenderTests(TestCase):
    """Full-stack check: sidebar renders on a real changelist page."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_superuser(username="root3", email="root3@example.com", password="x")
        self.client.force_login(self.user)

    def test_sidebar_lists_registered_apps(self):
        response = self.client.get("/admin/testapp/book/")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()
        self.assertIn("admin-home-sidebar", html)
        self.assertIn("data-toggle-favorite-url", html)
        self.assertIn("data-track-access-url", html)

    def test_star_toggle_reflected_after_favoriting(self):
        self.client.post("/admin/menu/toggle-favorite/", {"menu_key": "app.testapp"})
        response = self.client.get("/admin/testapp/book/")
        html = response.content.decode()
        self.assertIn("admin-home-nav-favorites", html)
