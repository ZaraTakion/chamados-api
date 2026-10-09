# CHM-501 — Celery e Redis

## Objetivo

Introduzir processamento assíncrono após estabilizar a API síncrona.
Redis é o broker Celery; o worker é um serviço independente no Docker Compose.
Na CHM-501, HTTP ainda não gerava eventos assíncronos. A CHM-502 introduz outbox transacional e um scheduler que processa eventos após commit, sem comunicar com Redis durante requisições.

## Arquitetura e segurança

- Broker Redis: database 0; resultados Redis: database 1.
- O worker Compose usa concorrência 1 para limitar consumo de RAM.
- Redis não publica porta externa; o volume redis_data é de desenvolvimento.
- JSON é o formato permitido para mensagens e resultados.
- Em produção, usar rede privada, credenciais seguras, TLS quando apropriado
  e retenção limitada. O env.example não contém credenciais de produção.

## Tarefa útil e idempotente

tickets.queue_summary contabiliza chamados por status usando uma consulta.
Retorna apenas total e contagens, sem texto de tickets, nomes ou identificadores
pessoais. É read-only, portanto repetir a execução não altera os registros.
Contagens podem mudar entre execuções caso novos tickets sejam criados.

## Como executar

Suba os serviços de desenvolvimento:

    docker compose up --build -d

Execute a tarefa pelo serviço API:

    docker compose exec api python manage.py shell -c "from tickets.tasks import ticket_queue_summary; r = ticket_queue_summary.delay(); print(r.get(timeout=15))"

Observe o worker:

    docker compose logs worker

Não chame result.get() dentro das views HTTP: bloquearia a requisição.
Sem Redis ativo, .delay() pode falhar; nenhum endpoint a chama nesta etapa.

## Retries e timeouts

OperationalError do banco ativa até 3 retries automáticos com backoff
exponencial e jitter. A tarefa tem soft time limit de 20 segundos e hard
time limit de 30 segundos. Se o broker falhar, a falha do envio precisa ser
tratada na origem. CHM-502 evita publicar diretamente no request: persiste
intenções de notificação na mesma transação e o worker periódico processa
somente eventos confirmados (ver NOTIFICATIONS.md).

## Testes e limites

Os testes validam contagens, consulta única, repetição sem efeitos colaterais,
modo eager sem Redis, conteúdo seguro do resultado e configuração de retry.
Modo eager comprova o código da tarefa, não o worker/broker real. A verificação
em Docker Compose é etapa distinta. Não são prometidas semânticas exactly-once
para tarefas futuras com efeitos colaterais.

## Aceite da CHM-501 — 08/10/2026

- CI: cinco jobs aprovados, incluindo worker real com Redis e PostgreSQL no Docker Compose. PostgreSQL 16 passou em 101 testes; a matriz SQLite encontrou 101, com 100 passando e 1 skip específico PostgreSQL; coverage CI 94,3%.
- Windows: Ruff e Django check aprovados; `makemigrations --check --dry-run` sem mudanças; 101 testes encontrados, 100 passaram, 1 skip específico PostgreSQL, 0 falhas, coverage **94,7%**.
- [PR #27 merged](https://github.com/ZaraTakion/chamados-api/pull/27), commit `49b549bc`.
- CHM-502 foi desenhada com outbox transacional, polling periódico após commit e entrega idempotente em inbox. A publicação não acontece dentro da requisição HTTP; ver NOTIFICATIONS.md.
