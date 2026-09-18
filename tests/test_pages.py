from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from django_admin_home.pages import build_custom_pages_group

CUSTOM_PAGES = [
    {
        "key": "page.dashboard",
        "name": "Dashboard",
        "icon": "gauge",
        "url_name": "admin:index",
        "new_tab": True,
    },
    {
        "key": "page.restricted",
        "name": "Restricted",
        "icon": "shield",
        "url_name": "admin:index",
        "permission": "auth.some_permission_nobody_has",
    },
]


class BuildCustomPagesGroupTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.staff = User.objects.create_user(username="staff", password="x", is_staff=True)
        self.superuser = User.objects.create_superuser(username="root", email="root@example.com", password="x")
        self.anon = type("Anon", (), {"is_authenticated": False})()

    def test_no_setting_returns_none(self):
        self.assertIsNone(build_custom_pages_group(self.staff))

    @override_settings(ADMIN_HOME_CUSTOM_PAGES=[])
    def test_empty_setting_returns_none(self):
        self.assertIsNone(build_custom_pages_group(self.staff))

    @override_settings(ADMIN_HOME_CUSTOM_PAGES=CUSTOM_PAGES)
    def test_anonymous_sees_nothing(self):
        self.assertIsNone(build_custom_pages_group(self.anon))

    @override_settings(ADMIN_HOME_CUSTOM_PAGES=CUSTOM_PAGES)
    def test_staff_sees_only_unrestricted_page(self):
        group = build_custom_pages_group(self.staff)
        self.assertIsNotNone(group)
        keys = [item["key"] for item in group["models"]]
        self.assertEqual(keys, ["page.dashboard"])

    @override_settings(ADMIN_HOME_CUSTOM_PAGES=CUSTOM_PAGES)
    def test_superuser_sees_every_page_regardless_of_permission(self):
        group = build_custom_pages_group(self.superuser)
        keys = [item["key"] for item in group["models"]]
        self.assertEqual(keys, ["page.dashboard", "page.restricted"])

    @override_settings(
        ADMIN_HOME_CUSTOM_PAGES=[{"key": "page.broken", "name": "Broken", "url_name": "admin:does-not-exist"}]
    )
    def test_unresolvable_route_is_skipped_not_raised(self):
        self.assertIsNone(build_custom_pages_group(self.staff))

    @override_settings(ADMIN_HOME_CUSTOM_PAGES=CUSTOM_PAGES)
    def test_favorite_flag_propagates(self):
        group = build_custom_pages_group(self.staff, favorites={"page.dashboard"})
        self.assertTrue(group["models"][0]["is_favorite"])
