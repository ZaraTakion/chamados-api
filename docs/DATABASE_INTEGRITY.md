# CHM-302 — Integridade relacional e PostgreSQL

## Objetivo

Analisar índices, consistência de dados e transações da Chamados API após as medições SQL do CHM-301. Este trabalho melhora integridade e compatibilidade do fluxo de atualização com PostgreSQL, sem declarar ganhos de latência que não foram medidos.

## Índices revisados

Na definição atual dos modelos, estão presentes:

| Tabela | Índices/recursos preexistentes | Consulta que motivou a revisão |
| --- | --- | --- |
| `tickets_ticket` | PK; índices de FK `requester_id` e `assignee_id`; `status`, `priority`, `created_at` (`db_index=True`) | Listagem do solicitante, filtros da equipe, ordenação por `-created_at, -id` |
| `tickets_ticketcomment` | PK; índice de FK `ticket_id`; `created_at` | Comentários por chamado e ordenação por `created_at, id` |
| `tickets_ticketauditevent` | PK; índices das FKs `ticket_id` e `actor_id`; `created_at` | Histórico por chamado, ordenação por `created_at, id` |

O CHM-301 mediu queries constantes com 1 e 20 registros e comprovou os JOINs de relacionamentos via `select_related` existentes. Essa medição **não demonstra** que adicionar índices compostos acelerará consultas em tabelas grandes.

**Decisão:** não criar índices compostos nesta entrega. Indexar indiscriminadamente aumenta espaço e custo de escrita. Primeiro precisamos de distribuição de dados e consultas representativas, volumes maiores e planos `EXPLAIN (ANALYZE, BUFFERS)` em PostgreSQL. Uma hipótese para futuro estudo seria `(requester_id, created_at DESC, id DESC)` pela listagem do solicitante. Hipótese não é ganho comprovado.

## Invariantes protegidas no banco

A migration `tickets/migrations/0003_database_integrity.py` acrescenta:

- `ticket_status_valid`: `status` só aceita `open`, `in_progress`, `waiting`, `resolved` e `closed`;
- `ticket_priority_valid`: `priority` só aceita `low`, `normal`, `high`, `urgent`;
- `ticket_audit_field_valid`: `TicketAuditEvent.field` só aceita `status`, `priority`, `assignee`.

Antes, as escolhas eram validadas na camada do Django/DRF, mas `QuerySet.update()` e scripts poderiam gravar valores inválidos diretamente no banco. Agora uma escrita inválida é barrada pelo próprio banco com `IntegrityError`. Os testes verificam valores inválidos e válidos em SQLite e PostgreSQL.

**Observação de migração:** constraints também verificam dados existentes quando instaladas. Se um ambiente mantiver registros inválidos anteriores à nova regra, a migração deve falhar e exigir correção explícita dos dados, nunca uma exclusão silenciosa. Faça backup antes de aplicar em qualquer banco com dados relevantes.

## Bloqueio transacional corrigido

A atualização do ticket já estava envolvida em `transaction.atomic`, com a gravação de histórico na mesma transação. No entanto, o queryset de atualização fazia `select_related("requester", "assignee")` e `select_for_update()`. O campo `assignee` é anulável, então o JOIN correspondente pode ser externo; PostgreSQL não permite bloquear o lado anulável de um OUTER JOIN com `FOR UPDATE`.

A atualização agora usa `select_for_update(of=("self",))` para bloquear **somente a linha do ticket**. O endpoint continua podendo ler os relacionamentos com `select_related`, sem tentar bloquear a tabela do responsável opcional.

Um teste específico, executado apenas no PostgreSQL, atualiza um ticket sem responsável e verifica que a mudança e os eventos de auditoria foram persistidos.

## Evidências de validação em CI

- GitHub Actions: PostgreSQL 16 real em contêiner de serviço.
- SQLite: Python 3.10, 3.11 e 3.12.
- 75 testes aprovados por ambiente; o teste PostgreSQL específico é pulado nas três execuções SQLite.
- Ruff, `manage.py check` e `makemigrations --check --dry-run` verdes.
- Coverage da aplicação: **95,2%**.
- Migração `0003_database_integrity` gerada e verificada quanto a mudanças pendentes.

## Aceite local — Windows / SQLite (08/10/2026)

- Backend local confirmado: `django.db.backends.sqlite3`.
- Backup consistente criado antes da migração; arquivo mantido localmente, fora do versionamento.
- `python manage.py migrate`: `Applying tickets.0003_database_integrity... OK`.
- Ruff, Django system check e `makemigrations --check --dry-run`: aprovados.
- `coverage run manage.py test`: 75 testes encontrados, 74 aprovados e 1 skip específico PostgreSQL, em 259.988s.
- `coverage report`: **95,8%**, 391 statements, 13 misses, 88 branches e 7 partial branches.
- PR #23 integrada por squash em 08/10/2026. A validação local cobre SQLite; a validação do bloqueio PostgreSQL foi feita no CI com PostgreSQL 16.

## Limites

- O job PostgreSQL roda em CI com dados de teste descartáveis, não representa produção.
- Não foram medidos ganhos de latência ou desempenho de índice. Evite prometer percentuais de aceleração.
- O bloqueio de linha protege atualizações transacionais feitas pelo endpoint; mutações diretas por outros caminhos não participam automaticamente do mesmo protocolo de locks/auditoria.
- A Sprint 04 / CHM-403 poderá ampliar o CI PostgreSQL com diferentes configurações, maior cobertura de cenários de deploy, concorrência e verificações operacionais.

## CHM-403 — Migrações explícitas e readiness no CI

A suíte PostgreSQL já criava um banco de testes isolado, com migrations gerenciadas pelo Django. CHM-403 acrescenta `migrate --noinput`, `migrate --check` e smoke test HTTP de readiness contra o banco PostgreSQL de CI antes da suíte. Ver [CI_POSTGRESQL.md](./CI_POSTGRESQL.md).
