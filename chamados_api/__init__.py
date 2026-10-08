"""Django project configuration for the support ticket API."""

from .celery import app as celery_app

__all__ = ("celery_app",)
