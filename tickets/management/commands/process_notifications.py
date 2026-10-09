"""Run the existing transactional notification outbox without Redis.

Intended only for local development/demo. Do not run in production or
alongside Celery Beat/worker processing the same database.
"""

import time

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import OperationalError, close_old_connections, connection

from tickets.tasks import deliver_pending_notifications


def _refresh_db_connection():
    # TestCase keeps an outer atomic block open; never close it mid-transaction.
    if not connection.in_atomic_block:
        close_old_connections()


class Command(BaseCommand):
    help = "Processa notificacoes locais sem Redis; use --watch para executar continuamente."

    def add_arguments(self, parser):
        parser.add_argument(
            "--watch",
            action="store_true",
            help="Repete a leitura da outbox a cada intervalo, ate Ctrl+C.",
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=30,
            help="Segundos entre ciclos no modo --watch (1 a 3600, padrao: 30).",
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError(
                "Comando disponivel somente com DJANGO_DEBUG=true; "
                "use Celery Worker e Beat em producao."
            )
        interval = options["interval"]
        if not 1 <= interval <= 3600:
            raise CommandError("--interval deve estar entre 1 e 3600 segundos.")

        watch = options["watch"]
        if watch:
            self.stdout.write("Processador local iniciado. Pressione Ctrl+C para encerrar.")
        try:
            while True:
                _refresh_db_connection()
                try:
                    result = deliver_pending_notifications.run()
                except OperationalError:
                    if not watch:
                        raise CommandError(
                            "Banco temporariamente indisponivel. Eventos permanecem na outbox."
                        ) from None
                    self.stderr.write("Banco indisponivel; o proximo ciclo tentara novamente.")
                else:
                    self.stdout.write(f"Notificacoes processadas: {result['processed']}")
                if not watch:
                    return
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write("Processador local encerrado.")
        finally:
            _refresh_db_connection()
