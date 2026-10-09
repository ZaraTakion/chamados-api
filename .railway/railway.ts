import {
  defineRailway,
  github,
  postgres,
  project,
  redis,
  service,
} from "railway/iac";

/**
 * CHM-601 — desired Railway infrastructure.
 *
 * Run `railway config plan` before any apply.
 * Project creation and apply may provision billable resources.
 * Secret values and allowed domains are managed as Railway shared variables.
 */
export default defineRailway((ctx) => {
  const db = postgres("Postgres");
  const broker = redis("Redis");
  const source = () => github("ZaraTakion/chamados-api", { branch: "main" });
  const commonEnv = {
    DJANGO_DEBUG: "false",
    DJANGO_SECRET_KEY: ctx.shared.DJANGO_SECRET_KEY,
    DJANGO_ALLOWED_HOSTS: ctx.shared.DJANGO_ALLOWED_HOSTS,
    DJANGO_SECURE_SSL_REDIRECT: "true",
    DJANGO_HSTS_SECONDS: "0",
    APP_LOG_LEVEL: "INFO",
    DATABASE_URL: db.env.DATABASE_URL,
    CELERY_BROKER_URL: broker.env.REDIS_URL,
    CELERY_RESULT_BACKEND: broker.env.REDIS_URL,
  };

  const web = service("chamados-api-web", {
    source: source(),
    preDeploy: "python manage.py migrate --noinput",
    healthcheck: "/api/health/ready/",
    healthcheckTimeout: 180,
    replicas: 1,
    env: commonEnv,
  });

  const worker = service("chamados-api-worker", {
    source: source(),
    start: "celery -A chamados_api worker --loglevel=INFO --concurrency=1",
    replicas: 1,
    env: commonEnv,
  });

  const beat = service("chamados-api-beat", {
    source: source(),
    start: "celery -A chamados_api beat --loglevel=INFO --schedule=/tmp/celerybeat-schedule",
    replicas: 1,
    env: commonEnv,
  });

  return project("chamados-api", {
    resources: [db, broker, web, worker, beat],
  });
});
