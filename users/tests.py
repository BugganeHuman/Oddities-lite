from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import get_user_model


User = get_user_model()

class TestAuth(APITestCase):

    def test_registration(self):
        data = {
        "username" : "Rabbit777",
        "email" : "honest_rabbit@gmail.com",
        "password" : "Password123-"
        }

        response = self.client.post('/api/users/register/', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="Rabbit777"))

    def test_login(self):
        User.objects.create_user(username="Rabbit777", password="Password123-",
            email="honest_rabbit@gmail.com")

        data = {
            "username" : "Rabbit777",
            "password" : "Password123-"
        }

        response = self.client.post("/api/users/auth/login/", data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)