"""Celery worker application for background ticket tasks."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chamados_api.settings")

app = Celery("chamados_api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
