from django.test import TestCase, override_settings

from django_admin_home.menu import (
    build_menu_tree,
    flatten_menu_items,
    icon_for_app,
    icon_for_model,
)

APP_LIST = [
    {
        "app_label": "buyers",
        "name": "Buyers",
        "app_url": "/admin/buyers/",
        "models": [
            {
                "object_name": "Buyer",
                "name": "Buyer",
                "admin_url": "/admin/buyers/buyer/",
                "add_url": "/admin/buyers/buyer/add/",
            }
        ],
    },
    {
        "app_label": "auth",
        "name": "Authentication",
        "app_url": "/admin/auth/",
        "models": [
            {
                "object_name": "User",
                "name": "User",
                "admin_url": "/admin/auth/user/",
                "add_url": "/admin/auth/user/add/",
            }
        ],
    },
]


class IconResolutionTests(TestCase):
    def test_builtin_default_for_unmapped_app(self):
        self.assertEqual(icon_for_app("unknown"), "folder")

    def test_builtin_default_for_unmapped_model(self):
        self.assertEqual(icon_for_model("unknown", "thing"), "list")

    def test_builtin_mapping_for_auth(self):
        self.assertEqual(icon_for_app("auth"), "shield")
        self.assertEqual(icon_for_model("auth", "User"), "user")

    @override_settings(ADMIN_HOME_APP_ICONS={"buyers": "building"})
    def test_settings_override_app_icon(self):
        self.assertEqual(icon_for_app("buyers"), "building")

    @override_settings(ADMIN_HOME_MODEL_ICONS={"buyers.buyer": "building"})
    def test_settings_override_model_icon(self):
        self.assertEqual(icon_for_model("buyers", "Buyer"), "building")

    @override_settings(ADMIN_HOME_APP_ICONS={"auth": "custom-shield"})
    def test_settings_override_merges_over_builtin(self):
        # Overridden app keeps the custom value...
        self.assertEqual(icon_for_app("auth"), "custom-shield")
        # ...while an unrelated builtin default (model-level) is untouched.
        self.assertEqual(icon_for_model("auth", "Group"), "users")


class BuildMenuTreeTests(TestCase):
    def test_tree_shape_and_default_icons(self):
        tree = build_menu_tree(APP_LIST)
        self.assertEqual(len(tree), 2)
        buyers_node = tree[0]
        self.assertEqual(buyers_node["key"], "app.buyers")
        self.assertEqual(buyers_node["icon"], "folder")
        self.assertFalse(buyers_node["is_favorite"])
        model_node = buyers_node["models"][0]
        self.assertEqual(model_node["key"], "buyers.buyer")
        self.assertEqual(model_node["url"], "/admin/buyers/buyer/")
        self.assertEqual(model_node["add_url"], "/admin/buyers/buyer/add/")

    def test_favorites_are_flagged(self):
        tree = build_menu_tree(APP_LIST, favorites={"app.buyers", "buyers.buyer"})
        buyers_node = tree[0]
        self.assertTrue(buyers_node["is_favorite"])
        self.assertTrue(buyers_node["models"][0]["is_favorite"])
        self.assertFalse(tree[1]["is_favorite"])

    @override_settings(ADMIN_HOME_APP_ICONS={"buyers": "building"})
    def test_uses_configured_icons(self):
        tree = build_menu_tree(APP_LIST)
        self.assertEqual(tree[0]["icon"], "building")
        self.assertEqual(tree[1]["icon"], "shield")  # builtin auth default


class FlattenMenuItemsTests(TestCase):
    def test_indexes_apps_and_models_with_parent(self):
        tree = build_menu_tree(APP_LIST)
        index = flatten_menu_items(tree)
        self.assertIn("app.buyers", index)
        self.assertIn("buyers.buyer", index)
        self.assertIsNone(index["app.buyers"]["parent"])
        self.assertEqual(index["buyers.buyer"]["parent"], "Buyers")
