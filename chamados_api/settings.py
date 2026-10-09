"""Settings for local development and environment-configured deployments."""

import os
from datetime import timedelta
from pathlib import Path

import dj_database_url

from chamados_api.deployment import validate_production_config

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.getenv("DJANGO_DEBUG", "true").lower() in {"1", "true", "yes"}
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "")
if not SECRET_KEY:
    if not DEBUG:
        raise RuntimeError("Set DJANGO_SECRET_KEY to a strong random secret in production.")
    SECRET_KEY = "dev-only-not-for-production-change-me"

ALLOWED_HOSTS = [host.strip() for host in os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,testserver").split(",") if host.strip()]
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "accounts",
    "tickets",
]

MIDDLEWARE = [
    "chamados_api.observability.RequestLoggingMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
SERVE_STATIC = os.getenv("DJANGO_SERVE_STATIC", "false").lower() in {"1", "true", "yes"}
if not DEBUG or SERVE_STATIC:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "chamados_api.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]
WSGI_APPLICATION = "chamados_api.wsgi.application"
ASGI_APPLICATION = "chamados_api.asgi.application"

database_url = os.getenv("DATABASE_URL")
if database_url:
    DATABASES = {"default": dj_database_url.parse(database_url, conn_max_age=600, ssl_require=not DEBUG)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": Path(os.getenv("SQLITE_PATH", BASE_DIR / "data" / "db.sqlite3")),
            "OPTIONS": {"timeout": 20},
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "chamados_api.errors.api_exception_handler",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {"anon": "30/hour", "user": "1200/day"},
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=20),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Chamados API",
    "DESCRIPTION": "API autenticada para abertura e acompanhamento de chamados de suporte.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}

if not DEBUG:
    SECURE_SSL_REDIRECT = os.getenv("DJANGO_SECURE_SSL_REDIRECT", "true").lower() in {"1", "true", "yes"}
    validate_production_config(
        debug=DEBUG,
        secret_key=SECRET_KEY,
        allowed_hosts=ALLOWED_HOSTS,
        explicit_hosts=bool(os.getenv("DJANGO_ALLOWED_HOSTS", "").strip()),
        database_url=database_url,
        ssl_redirect=SECURE_SSL_REDIRECT,
    )
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    # Enable only behind a trusted reverse proxy that strips client-supplied headers.
    if os.getenv("DJANGO_TRUST_PROXY_SSL_HEADER", "false").lower() in {"1", "true", "yes"}:
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# CHM-401: minimal JSON logs; request bodies, query strings and credentials are excluded.
# Local test runs are quiet by default; production emits request completion metadata.
APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "WARNING" if DEBUG else "INFO").upper()
if APP_LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
    raise ValueError("APP_LOG_LEVEL must be DEBUG, INFO, WARNING, ERROR or CRITICAL")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "safe_json": {"()": "chamados_api.observability.SafeJSONFormatter"},
    },
    "handlers": {
        "safe_console": {
            "class": "logging.StreamHandler",
            "formatter": "safe_json",
        },
    },
    "loggers": {
        "chamados_api.http": {
            "handlers": ["safe_console"],
            "level": APP_LOG_LEVEL,
            "propagate": False,
        },
        # The default Django request/security messages may include raw URLs
        # or exception text. Serialize only allowlisted fields instead.
        "django.request": {
            "handlers": ["safe_console"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["safe_console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}

# CHM-502: HTTP persists outbox rows only; Celery Beat processes them after commit.
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://127.0.0.1:6379/1")
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_TRACK_STARTED = True
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_DEFAULT_QUEUE = "tickets"
CELERY_TASK_SOFT_TIME_LIMIT = 20
CELERY_TASK_TIME_LIMIT = 30

# The worker scans only committed outbox entries. No broker I/O occurs in HTTP.
CELERY_BEAT_SCHEDULE = {
    "deliver-notification-outbox": {
        "task": "tickets.deliver_pending_notifications",
        "schedule": 30.0,
    },
}
