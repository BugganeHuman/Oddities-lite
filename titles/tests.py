from rest_framework.test import APITestCase
from rest_framework import status
from .models import Title
from django.contrib.auth import get_user_model


User = get_user_model()

class TitleApiTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='Rabbit777', password='Password123-')
        self.title = Title.objects.create(name="Ozark", year_start=2017, director="J",
            category="SR", cover="https://media.themoviedb.org/t/p/"
            "w300_and_h450_face/pCGyPVrI9Fzw6rE1Pvi4BIXF6ET.jpg",
            start_watch="2026-03-03", end_watch="2026-03-04", status="DONE",
            review="ok 6.5", rating=6.5, owner=self.user)
        self.url = f'/api/titles/title/{self.title.id}/'

    def test_create(self):
        self.client.force_authenticate(user=self.user)
        el = {
            "name": "Ozark",
            "year_start": 2017,
            "year_end": "",
            "director": "",
            "category": "SR",
            "cover": "",
            "start_watch": "2026-03-01",
            "end_watch": "2026-03-03",
            "status": "DONE",
            "review": "ok 6.5",
            "rating": "6.5",
            "owner": self.user
        }

        act = self.client.post("/api/titles/title/", el)

        self.assertEqual(act.status_code, 201)
        #self.assertEqual(Title.objects.count(), 2)

    def test_delete(self):
        self.client.force_authenticate (user= self.user)

        response = self.client.delete(f"/api/titles/title/{self.title.id}/")

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Title.objects.filter(id=self.title.id).exists())
        # self.assertEqual(Title.objects.count(), 0)

    def test_update(self):
        self.client.force_authenticate(user= self.user)
        new_data = {'director': 'q'}
        response = self.client.patch(self.url, new_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.title.refresh_from_db()

        self.assertEqual(self.title.director, 'q')
