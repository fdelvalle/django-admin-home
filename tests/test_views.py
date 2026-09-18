from django.contrib.auth import get_user_model
from django.test import TestCase

from django_admin_home.models import MenuAccess, MenuFavorite


class ToggleFavoriteViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="staff", password="x", is_staff=True)
        self.client.force_login(self.user)

    def test_creates_favorite(self):
        response = self.client.post("/admin/menu/toggle-favorite/", {"menu_key": "buyers.buyer"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"menu_key": "buyers.buyer", "is_favorite": True})
        self.assertTrue(MenuFavorite.objects.filter(user=self.user, menu_key="buyers.buyer").exists())

    def test_toggling_twice_removes_favorite(self):
        self.client.post("/admin/menu/toggle-favorite/", {"menu_key": "buyers.buyer"})
        response = self.client.post("/admin/menu/toggle-favorite/", {"menu_key": "buyers.buyer"})
        self.assertEqual(response.json(), {"menu_key": "buyers.buyer", "is_favorite": False})
        self.assertFalse(MenuFavorite.objects.filter(user=self.user, menu_key="buyers.buyer").exists())

    def test_missing_menu_key_is_bad_request(self):
        response = self.client.post("/admin/menu/toggle-favorite/", {})
        self.assertEqual(response.status_code, 400)

    def test_requires_post(self):
        response = self.client.get("/admin/menu/toggle-favorite/")
        self.assertEqual(response.status_code, 405)


class TrackAccessViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="staff2", password="x", is_staff=True)
        self.client.force_login(self.user)

    def test_creates_access_with_count_one(self):
        response = self.client.post("/admin/menu/track-access/", {"menu_key": "buyers.buyer"})
        self.assertEqual(response.status_code, 200)
        access = MenuAccess.objects.get(user=self.user, menu_key="buyers.buyer")
        self.assertEqual(access.access_count, 1)

    def test_repeated_access_increments_count(self):
        self.client.post("/admin/menu/track-access/", {"menu_key": "buyers.buyer"})
        self.client.post("/admin/menu/track-access/", {"menu_key": "buyers.buyer"})
        access = MenuAccess.objects.get(user=self.user, menu_key="buyers.buyer")
        self.assertEqual(access.access_count, 2)

    def test_missing_menu_key_is_bad_request(self):
        response = self.client.post("/admin/menu/track-access/", {})
        self.assertEqual(response.status_code, 400)
