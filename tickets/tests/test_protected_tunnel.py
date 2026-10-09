"""Safety contract for temporary Cloudflare previews (no external network)."""

import os
import subprocess
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings

from chamados_api.deployment import (
    validate_production_config,
    validate_protected_preview_config,
)
from scripts.protected_preview import (
    check_cloudflared_version,
    preview_environment,
    validate_email,
)
from tickets.models import NotificationOutbox, TicketNotification

ROOT = Path(__file__).resolve().parents[2]


class ProtectedTunnelSecurityTests(SimpleTestCase):
    def setUp(self):
        self.conf = {
            "debug": False,
            "secret_key": "S3cure!pR4nd0m" * 5,
            "allowed_hosts": ["violet-echo.trycloudflare.com"],
            "database_url": None,
            "ssl_redirect": True,
            "sqlite_path": ROOT / "data" / "protected-preview.sqlite3",
            "base_dir": ROOT,
        }

    def test_valid_isolated_protected_tunnel(self):
        validate_protected_preview_config(**self.conf)

    def test_cannot_use_debug_local_db_public_wildcard_or_password_placeholder(self):
        cases = [
            {"debug": True},
            {"database_url": "postgresql://user:password@example.com/database"},
            {"ssl_redirect": False},
            {"allowed_hosts": ["*"]},
            {"allowed_hosts": [".trycloudflare.com"]},
            {"allowed_hosts": ["a.trycloudflare.com", "b.trycloudflare.com"]},
            {"allowed_hosts": ["api.example.com"]},
            {"sqlite_path": ROOT / "data" / "db.sqlite3"},
            {"secret_key": "dev-only-DO-NOT-USE" * 9},
        ]
        for updates in cases:
            with self.subTest(updates=updates), self.assertRaises(ImproperlyConfigured):
                validate_protected_preview_config(**{**self.conf, **updates})

    def test_standard_production_still_rejects_sqlite(self):
        with self.assertRaises(ImproperlyConfigured):
            validate_production_config(
                debug=False,
                secret_key=self.conf["secret_key"],
                allowed_hosts=self.conf["allowed_hosts"],
                explicit_hosts=True,
                database_url=None,
                ssl_redirect=True,
            )

    def test_requires_cloudflared_with_protected_email_support(self):
        check_cloudflared_version("cloudflared version 2026.9.3 (built)")
        check_cloudflared_version("cloudflared version 2027.1.0")
        for version in ("cloudflared version 2026.9.2", "cloudflared version 2025.12.10", "garbage"):
            with self.subTest(version=version), self.assertRaises(ValueError):
                check_cloudflared_version(version)

    def test_email_allowlist_rejects_wildcards_and_injection(self):
        self.assertEqual(validate_email("demo@example.com"), "demo@example.com")
        for value in ("", "*@example.com", "bad email@example.com", "-x", "a@localhost", "a@example.com,b@example.org"):
            with self.subTest(email=value), self.assertRaises(ValueError):
                validate_email(value)

    def test_preview_env_isolates_secrets_and_database(self):
        env = preview_environment(
            {
                "DATABASE_URL": "postgresql://confidential:secret@db.example.com/private",
                "DJANGO_SECRET_KEY": "sensitive-original-secret",
                "DJANGO_DEBUG": "true",
                "DJANGO_ALLOWED_HOSTS": "localhost",
                "DJANGO_TRUST_PROXY_SSL_HEADER": "true",
            },
            "violet-echo.trycloudflare.com",
        )
        self.assertNotIn("DATABASE_URL", env)
        self.assertNotIn("sensitive-original-secret", str(env))
        self.assertEqual(env["DJANGO_DEBUG"], "false")
        self.assertEqual(env["DJANGO_PROTECTED_PREVIEW"], "true")
        self.assertEqual(env["DJANGO_ALLOWED_HOSTS"], "violet-echo.trycloudflare.com")
        self.assertEqual(env["DJANGO_TRUST_PROXY_SSL_HEADER"], "false")
        self.assertEqual(env["DJANGO_SECURE_SSL_REDIRECT"], "true")
        self.assertEqual(env["SQLITE_PATH"], str(ROOT / "data" / "protected-preview.sqlite3"))
        self.assertGreaterEqual(len(env["DJANGO_SECRET_KEY"]), 50)
        self.assertNotEqual(env["DJANGO_SECRET_KEY"], preview_environment({}, "violet-echo.trycloudflare.com")["DJANGO_SECRET_KEY"])

    def test_preview_settings_imports_with_preview_db_without_production_bypass(self):
        env = preview_environment(os.environ, "violet-echo.trycloudflare.com")
        result = subprocess.run(
            [
                sys.executable, "-c",
                "from django.conf import settings; "
                "assert settings.PROTECTED_PREVIEW; "
                "assert settings.DEBUG is False; "
                "assert settings.ALLOWED_HOSTS == ['violet-echo.trycloudflare.com']; "
                "assert settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'; "
                "assert settings.SECURE_SSL_REDIRECT is True",
            ],
            cwd=ROOT, env=env, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr[:500])

    def test_preview_rejects_unsafe_settings_at_startup(self):
        for change in (
            {"DJANGO_DEBUG": "true"},
            {"SQLITE_PATH": str(ROOT / "data" / "db.sqlite3")},
            {"DJANGO_ALLOWED_HOSTS": "*.trycloudflare.com"},
            {"DATABASE_URL": "postgresql://user:pass@db.example.com/demo"},
        ):
            with self.subTest(change=list(change)):
                env = preview_environment(os.environ, "violet-echo.trycloudflare.com")
                env.update(change)
                r = subprocess.run(
                    [sys.executable, "-c", "import chamados_api.settings"],
                    cwd=ROOT, env=env, capture_output=True, text=True, check=False,
                )
                self.assertNotEqual(r.returncode, 0)
                self.assertNotIn("user:pass", r.stderr)


@override_settings(DEBUG=False, PROTECTED_PREVIEW=True)
class ProtectedTunnelOfflineProcessorTests(TestCase):
    def test_offline_processor_allowed_only_in_isolated_preview(self):
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.create_user(username="preview-test-user")
        NotificationOutbox.objects.create(
            recipient=user, kind=NotificationOutbox.Kind.CREATED,
            ticket_reference="CH-000001",
        )
        out = StringIO()
        call_command("process_notifications", stdout=out)
        self.assertEqual(TicketNotification.objects.count(), 1)
        self.assertIn("Notificacoes processadas: 1", out.getvalue())
        with override_settings(PROTECTED_PREVIEW=False):
            from django.core.management.base import CommandError

            with self.assertRaises(CommandError):
                call_command("process_notifications", stdout=StringIO())

    def test_preview_mode_does_not_send_to_redis(self):
        out = StringIO()
        with patch("tickets.tasks.deliver_pending_notifications.delay") as sender:
            call_command("process_notifications", stdout=out)
        sender.assert_not_called()
