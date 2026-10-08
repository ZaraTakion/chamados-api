"""CHM-402: health probes, readiness isolation and production safety checks."""

import os
import subprocess
import sys
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.db import OperationalError, connection
from django.test import SimpleTestCase, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework.test import APIClient

from chamados_api.deployment import validate_production_config


class HealthProbeTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_liveness_and_legacy_endpoint_are_public_and_uncached(self):
        for route in ("health", "health-live"):
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["status"], "ok")
            self.assertIn("timestamp", response.data)
            self.assertEqual(response["Cache-Control"], "no-store")
            self.assertRegex(response["X-Request-ID"], r"^[0-9a-f]{32}$")

    def test_liveness_does_not_probe_database(self):
        with patch("chamados_api.health.connections") as db:
            response = self.client.get(reverse("health-live"))
            self.assertEqual(response.status_code, 200)
            db.__getitem__.assert_not_called()

    def test_readiness_returns_503_without_leaking_database_errors(self):
        with patch("chamados_api.health.connections") as db:
            db.__getitem__.return_value.cursor.side_effect = OperationalError("private-db-host password")
            response = self.client.get(reverse("health-ready"))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["status"], "unavailable")
        self.assertIn("timestamp", response.data)
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertRegex(response["X-Request-ID"], r"^[0-9a-f]{32}$")
        self.assertNotIn("private-db-host", str(response.data))
        self.assertNotIn("password", str(response.data))

    def test_readiness_fails_closed_on_unexpected_probe_result(self):
        with patch("chamados_api.health.connections") as db:
            db.__getitem__.return_value.cursor.return_value.__enter__.return_value.fetchone.return_value = (0,)
            response = self.client.get(reverse("health-ready"))
        self.assertEqual(response.status_code, 503)

    def test_health_probes_ignore_normal_anonymous_request_throttling(self):
        for _ in range(35):
            self.assertEqual(self.client.get(reverse("health-live")).status_code, 200)
        self.assertEqual(self.client.get(reverse("health")).status_code, 200)


class DatabaseReadinessTests(TestCase):
    def test_ready_performs_one_database_query(self):
        with CaptureQueriesContext(connection) as captured:
            response = self.client.get(reverse("health-ready"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "ok")
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(len(captured), 1)
        self.assertIn("SELECT 1", captured[0]["sql"])

    def test_schema_exposes_both_new_probes(self):
        response = self.client.get(reverse("schema"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("/api/health/", response.data["paths"])
        self.assertIn("/api/health/live/", response.data["paths"])
        self.assertIn("/api/health/ready/", response.data["paths"])


class DeploymentGuardTests(SimpleTestCase):
    def setUp(self):
        self.good = {
            "debug": False,
            "secret_key": "S3cure!" * 12 + "ExtraRandom",
            "allowed_hosts": ["api.example.com"],
            "explicit_hosts": True,
            "database_url": "postgresql://service:dummy@db.example.com:5432/app",
            "ssl_redirect": True,
        }

    def test_valid_production_configuration(self):
        validate_production_config(**self.good)

    def test_local_development_is_not_restricted(self):
        local = {**self.good, "debug": True, "secret_key": "", "allowed_hosts": [], "explicit_hosts": False,
                 "database_url": "", "ssl_redirect": False}
        validate_production_config(**local)

    def test_production_rejects_weak_and_placeholder_keys(self):
        for secret in ("", "short", "dev-only-" + "aB39-_" * 15, "django-insecure-" + "A9_!" * 15, "a" * 70):
            with self.subTest(secret_length=len(secret)):
                with self.assertRaises(ImproperlyConfigured):
                    validate_production_config(**{**self.good, "secret_key": secret})

    def test_production_rejects_missing_and_wildcard_hosts(self):
        for hosts, explicit in [([], False), (["api.example.com"], False), ([], True), (["*"], True)]:
            with self.subTest(hosts=hosts, explicit=explicit):
                with self.assertRaises(ImproperlyConfigured):
                    validate_production_config(**{**self.good, "allowed_hosts": hosts, "explicit_hosts": explicit})

    def test_production_requires_postgresql(self):
        for url in ("", "sqlite:///tmp/app.sqlite3", "mysql://user@host/db"):
            with self.subTest(url=url):
                with self.assertRaises(ImproperlyConfigured):
                    validate_production_config(**{**self.good, "database_url": url})

    def test_production_requires_https_redirect(self):
        with self.assertRaises(ImproperlyConfigured):
            validate_production_config(**{**self.good, "ssl_redirect": False})

    def test_settings_import_fails_early_with_unsafe_production_configuration(self):
        env = dict(os.environ)
        env.update({
            "DJANGO_DEBUG": "false",
            "DJANGO_SECRET_KEY": "short",
            "DJANGO_ALLOWED_HOSTS": "api.example.com",
            "DATABASE_URL": self.good["database_url"],
            "DJANGO_SECURE_SSL_REDIRECT": "true",
        })
        result = subprocess.run(
            [sys.executable, "-c", "import chamados_api.settings"],
            env=env, capture_output=True, text=True, check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ImproperlyConfigured", result.stderr)
        self.assertNotIn(self.good["database_url"], result.stderr)
