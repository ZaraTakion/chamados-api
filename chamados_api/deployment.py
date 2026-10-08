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
