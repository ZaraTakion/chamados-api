from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from tickets.tests.base import APITestBase

User = get_user_model()


class AuthenticationAPITests(APITestBase):
    def test_registration_normalizes_email_hashes_password_and_returns_no_password(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "nova-pessoa",
                "email": " NEW@example.com ",
                "password": "Other-strong-test-pass-2026!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        account = User.objects.get(username="nova-pessoa")
        self.assertEqual(account.email, "new@example.com")
        self.assertTrue(account.check_password("Other-strong-test-pass-2026!"))
        self.assertNotIn("password", response.data)

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "duplicada",
                "email": "REQUESTER@example.com",
                "password": "Other-strong-test-pass-2026!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            reverse("register"),
            {"username": "fraca", "email": "weak@example.com", "password": "1234567890"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_me_requires_authentication_and_returns_current_user(self):
        unauthorized = self.client.get(reverse("me"))
        self.assertEqual(unauthorized.status_code, status.HTTP_401_UNAUTHORIZED)

        self.authenticate(self.requester)
        response = self.client.get(reverse("me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.requester.username)
        self.assertEqual(response.data["email"], self.requester.email)
        self.assertFalse(response.data["is_staff"])

    def test_refresh_rotates_token_and_blacklist_revokes_refresh(self):
        pair = self.client.post(
            reverse("token_obtain_pair"),
            {"username": self.requester.username, "password": self.password},
            format="json",
        )
        self.assertEqual(pair.status_code, status.HTTP_200_OK)

        original_refresh = pair.data["refresh"]
        rotated = self.client.post(
            reverse("token_refresh"),
            {"refresh": original_refresh},
            format="json",
        )
        self.assertEqual(rotated.status_code, status.HTTP_200_OK)
        self.assertIn("access", rotated.data)
        self.assertIn("refresh", rotated.data)

        reused_original = self.client.post(
            reverse("token_refresh"),
            {"refresh": original_refresh},
            format="json",
        )
        self.assertEqual(reused_original.status_code, status.HTTP_401_UNAUTHORIZED)

        new_refresh = rotated.data["refresh"]
        blacklisted = self.client.post(
            reverse("token_blacklist"),
            {"refresh": new_refresh},
            format="json",
        )
        self.assertEqual(blacklisted.status_code, status.HTTP_200_OK)

        reused_blacklisted = self.client.post(
            reverse("token_refresh"),
            {"refresh": new_refresh},
            format="json",
        )
        self.assertEqual(reused_blacklisted.status_code, status.HTTP_401_UNAUTHORIZED)
