ARG PYTHON_BASE_IMAGE=python:3.12-slim
FROM ${PYTHON_BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app
COPY requirements.txt .
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt
COPY --chown=app:app . .
RUN python manage.py collectstatic --noinput

USER app
EXPOSE 8000
CMD ["sh", "-c", "gunicorn chamados_api.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2} --access-logfile - --error-logfile -"]
