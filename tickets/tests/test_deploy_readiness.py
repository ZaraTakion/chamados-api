"""CHM-601: deployment manifests and safe public smoke checks."""

import json
from pathlib import Path

from django.test import Client, SimpleTestCase, override_settings

from scripts.smoke_deploy import validate_base_url

ROOT = Path(__file__).resolve().parents[2]


class RailwayDeploymentConfigTests(SimpleTestCase):
    def _read(self, name):
        return json.loads((ROOT / "deploy" / name).read_text(encoding="utf-8"))

    def test_web_service_runs_migrations_and_requires_readiness(self):
        conf = self._read("railway-web.json")
        self.assertEqual(conf["build"]["builder"], "DOCKERFILE")
        self.assertEqual(conf["deploy"]["preDeployCommand"], "python manage.py migrate --noinput")
        self.assertEqual(conf["deploy"]["healthcheckPath"], "/api/health/ready/")
        self.assertGreaterEqual(conf["deploy"]["healthcheckTimeout"], 120)

    def test_worker_and_beat_have_independent_start_commands(self):
        worker = self._read("railway-worker.json")
        beat = self._read("railway-beat.json")
        self.assertIn("celery -A chamados_api worker", worker["deploy"]["startCommand"])
        self.assertIn("celery -A chamados_api beat", beat["deploy"]["startCommand"])
        self.assertNotIn("preDeployCommand", worker["deploy"])
        self.assertNotIn("preDeployCommand", beat["deploy"])
        self.assertNotIn("healthcheckPath", worker["deploy"])
        self.assertNotIn("healthcheckPath", beat["deploy"])

    def test_docker_context_excludes_secrets_and_local_backups(self):
        patterns = (ROOT / ".dockerignore").read_text(encoding="utf-8").splitlines()
        for pattern in (".env", ".env.*", "data/", "*.sqlite3", "*.dump", "*.backup", ".coverage*"):
            self.assertIn(pattern, patterns)

    def test_smoke_rejects_credentials_in_url_and_public_http(self):
        for invalid in (
            "http://api.example.com", "https://user:pw@api.example.com",
            "https://api.example.com/api", "https://api.example.com?token=123",
            "http://127.0.0.1:8000",
        ):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    validate_base_url(invalid)

    def test_smoke_accepts_only_https_or_opted_in_loopback(self):
        self.assertEqual(validate_base_url("https://api.example.com/"), "https://api.example.com")
        self.assertEqual(
            validate_base_url("http://127.0.0.1:8000/", allow_http_local=True),
            "http://127.0.0.1:8000",
        )
        with self.assertRaises(ValueError):
            validate_base_url("http://example.com", allow_http_local=True)

    @override_settings(
        DEBUG=False,
        SECURE_SSL_REDIRECT=True,
        SECURE_REDIRECT_EXEMPT=[r"^api/health/(?:live|ready)/$"],
        ALLOWED_HOSTS=["testserver"],
    )
    def test_private_http_healthcheck_is_available_but_api_redirects(self):
        client = Client()
        live = client.get("/api/health/live/")
        self.assertEqual(live.status_code, 200)
        other = client.get("/api/auth/me/")
        self.assertEqual(other.status_code, 301)
        self.assertEqual(other["Location"], "https://testserver/api/auth/me/")
