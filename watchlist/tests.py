from rest_framework.test import APITestCase
from rest_framework import status
from .models import WatchlistItem
from django.contrib.auth import get_user_model


User = get_user_model()

class WatchlistTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="Rabbit777", password="Password123-")
        self.item = WatchlistItem.objects.create(name="Mr.Robot", year_start=2015,
            category="SR", owner=self.user)
        self.url = f'/api/watchlist/item/{self.item.id}/'

    def test_create(self):
        self.client.force_authenticate(user=self.user)

        el = {
        "name": "Ozark",
        "year_start": 2017,
        "category": "SR",
        "owner" : self.user
        }
        response = self.client.post("/api/watchlist/item/", el)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete(self):
        self.client.force_authenticate(user= self.user)

        response = self.client.delete(self.url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(WatchlistItem.objects.filter(id=self.item.id))

    def test_update(self):
        self.client.force_authenticate(user= self.user)

        new_data = {'name' : 'test'}
        response = self.client.patch(self.url, new_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.item.refresh_from_db()

        self.assertEqual(self.item.name, 'test')