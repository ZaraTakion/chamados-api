"""CHM-601: deployment infrastructure and safe public smoke checks."""

from pathlib import Path

from django.test import Client, SimpleTestCase, override_settings

from scripts.smoke_deploy import validate_base_url

ROOT = Path(__file__).resolve().parents[2]


class RailwayDeploymentConfigTests(SimpleTestCase):
    def _iac(self):
        return (ROOT / ".railway" / "railway.ts").read_text(encoding="utf-8")

    def test_current_infrastructure_as_code_replaces_deprecated_files(self):
        code = self._iac()
        self.assertIn('from "railway/iac"', code)
        self.assertIn('postgres("Postgres")', code)
        self.assertIn('redis("Redis")', code)
        self.assertIn('github("ZaraTakion/chamados-api"', code)
        for old in ("railway-web.json", "railway-worker.json", "railway-beat.json"):
            self.assertFalse((ROOT / "deploy" / old).exists())

    def test_web_service_runs_migrations_and_requires_readiness(self):
        code = self._iac()
        self.assertIn('service("chamados-api-web"', code)
        self.assertIn('preDeploy: "python manage.py migrate --noinput"', code)
        self.assertIn('healthcheck: "/api/health/ready/"', code)
        self.assertIn("healthcheckTimeout: 180", code)

    def test_worker_and_beat_have_independent_start_commands(self):
        code = self._iac()
        self.assertIn('service("chamados-api-worker"', code)
        self.assertIn('service("chamados-api-beat"', code)
        self.assertIn('start: "celery -A chamados_api worker', code)
        self.assertIn('start: "celery -A chamados_api beat', code)
        self.assertEqual(code.count("preDeploy:"), 1)
        self.assertEqual(code.count("healthcheck:"), 1)

    def test_production_credentials_are_railway_shared_variables(self):
        code = self._iac()
        self.assertIn("DJANGO_SECRET_KEY: ctx.shared.DJANGO_SECRET_KEY", code)
        self.assertIn("DJANGO_ALLOWED_HOSTS: ctx.shared.DJANGO_ALLOWED_HOSTS", code)
        self.assertIn("DATABASE_URL: db.env.DATABASE_URL", code)
        self.assertIn("CELERY_BROKER_URL: broker.env.REDIS_URL", code)
        self.assertNotIn("chamados-local-only", code)

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
