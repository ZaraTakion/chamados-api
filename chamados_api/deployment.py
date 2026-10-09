"""Fail-closed validation of production settings without disclosing secrets."""

from django.core.exceptions import ImproperlyConfigured


def validate_production_config(
    *,
    debug,
    secret_key,
    allowed_hosts,
    explicit_hosts,
    database_url,
    ssl_redirect,
):
    """Enforce safe deployment prerequisites; development remains unaffected."""
    if debug:
        return

    if (
        len(secret_key) < 50
        or secret_key.startswith(("dev-only", "replace-", "django-insecure-"))
        or len(set(secret_key)) < 12
    ):
        raise ImproperlyConfigured("DJANGO_SECRET_KEY must be a strong random secret in production.")

    if not explicit_hosts or not allowed_hosts or "*" in allowed_hosts:
        raise ImproperlyConfigured("Set DJANGO_ALLOWED_HOSTS explicitly without a wildcard in production.")

    if not database_url or not database_url.startswith(("postgresql://", "postgres://")):
        raise ImproperlyConfigured("Set DATABASE_URL to a persistent PostgreSQL database in production.")

    if not ssl_redirect:
        raise ImproperlyConfigured("DJANGO_SECURE_SSL_REDIRECT must be true in production.")


def validate_protected_preview_config(
    *,
    debug,
    secret_key,
    allowed_hosts,
    database_url,
    ssl_redirect,
    sqlite_path,
    base_dir,
):
    """Fail closed for one email-protected trycloudflare.com preview.

    This *never* relaxes standard production deployment validation.
    The preview has an isolated SQLite DB and explicitly configured host.
    """
    import re
    from pathlib import Path

    if debug or database_url or not ssl_redirect:
        raise ImproperlyConfigured(
            "Protected preview requires DEBUG=false, isolated SQLite and HTTPS redirect."
        )
    if (
        len(secret_key) < 50
        or len(set(secret_key)) < 12
        or secret_key.startswith(("dev-only", "replace-", "django-insecure-"))
    ):
        raise ImproperlyConfigured("Protected preview requires an ephemeral strong secret.")
    if len(allowed_hosts) != 1 or not re.fullmatch(
        r"[a-z0-9-]+\.trycloudflare\.com", allowed_hosts[0], flags=re.ASCII
    ):
        raise ImproperlyConfigured("Protected preview requires one exact trycloudflare.com hostname.")
    expected = (Path(base_dir) / "data" / "protected-preview.sqlite3").resolve()
    if Path(sqlite_path).resolve() != expected:
        raise ImproperlyConfigured("Protected preview must use its isolated demo SQLite database.")
