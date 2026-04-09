from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.test import APITestCase

from apps.accounts.models import LoginAttempt

User = get_user_model()


class AuthApiTestCase(APITestCase):
    def setUp(self):
        self.login_url = reverse("accounts:auth-login")
        self.refresh_url = reverse("accounts:auth-refresh")
        self.logout_url = reverse("accounts:auth-logout")
        self.me_url = reverse("accounts:auth-me")
        self.user_password = "Passw0rd!123"
        self.user = User.objects.create_user(
            email="verified@test.com",
            password=self.user_password,
            email_verified=True,
            first_name="Ada",
            last_name="Lovelace",
        )

    def _auth_headers(self, user):
        access = str(AccessToken.for_user(user))
        return {"HTTP_AUTHORIZATION": f"Bearer {access}"}

    def test_login_success_returns_access_and_refresh(self):
        response = self.client.post(
            self.login_url,
            {"email": self.user.email, "password": self.user_password},
            format="json",
            REMOTE_ADDR="127.0.0.10",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_invalid_credentials_returns_401_and_tracks_attempt(self):
        response = self.client.post(
            self.login_url,
            {"email": self.user.email, "password": "wrong-password"},
            format="json",
            REMOTE_ADDR="127.0.0.11",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(
            LoginAttempt.objects.filter(
                email=self.user.email,
                ip_address="127.0.0.11",
                success=False,
            ).exists()
        )

    def test_login_blocks_after_failed_threshold_with_429(self):
        for _ in range(5):
            LoginAttempt.objects.create(
                email=self.user.email,
                ip_address="127.0.0.12",
                success=False,
            )

        response = self.client.post(
            self.login_url,
            {"email": self.user.email, "password": self.user_password},
            format="json",
            REMOTE_ADDR="127.0.0.12",
        )

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_login_denies_user_when_email_is_not_verified(self):
        unverified_user = User.objects.create_user(
            email="unverified@test.com",
            password=self.user_password,
            email_verified=False,
        )

        response = self.client.post(
            self.login_url,
            {"email": unverified_user.email, "password": self.user_password},
            format="json",
            REMOTE_ADDR="127.0.0.13",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_me_returns_profile_for_authenticated_user(self):
        response = self.client.get(
            self.me_url,
            format="json",
            **self._auth_headers(self.user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertNotIn("is_staff", response.data)

    def test_me_returns_401_for_anonymous_user(self):
        response = self.client.get(self.me_url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_valid_refresh_revokes_token(self):
        refresh = str(RefreshToken.for_user(self.user))

        logout_response = self.client.post(
            self.logout_url,
            {"refresh": refresh},
            format="json",
            **self._auth_headers(self.user),
        )
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        refresh_response = self.client.post(
            self.refresh_url,
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_invalid_refresh_returns_400(self):
        response = self.client.post(
            self.logout_url,
            {"refresh": "invalid-token"},
            format="json",
            **self._auth_headers(self.user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_requires_authentication(self):
        refresh = str(RefreshToken.for_user(self.user))
        response = self.client.post(
            self.logout_url,
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_does_not_require_authenticated_user(self):
        refresh = str(RefreshToken.for_user(self.user))
        response = self.client.post(
            self.refresh_url,
            {"refresh": refresh},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
