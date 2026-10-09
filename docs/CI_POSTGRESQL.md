# CHM-403 — Matriz SQLite e PostgreSQL

## Pipeline

O GitHub Actions valida SQLite em Python 3.10, 3.11 e 3.12 e PostgreSQL 16
real iniciado como serviço nativo PostgreSQL 16 do runner Ubuntu (sem
pull de imagem Docker Hub). Ambos verificam Ruff, Django system check,
migrations e a suíte completa. O job PostgreSQL aplica migrations no banco do
CI, confirma que não há migrations pendentes e executa GET /api/health/ready/
contra o banco real. Então inicia a suíte Django, que cria um banco temporário
separado e aplica suas próprias migrations.

## Diferenças verificadas

| Cenário | SQLite | PostgreSQL 16 |
| --- | --- | --- |
| Check constraints de domínio | Sim | Sim |
| Operações de tickets e auditoria | Sim | Sim |
| Row locking select_for_update | Não reproduz semântica PG | Teste específico executado |
| Teste com assignee nulo e row lock | Ignorado intencionalmente | Executado |
| Readiness / SELECT 1 | Sim | Sim |
| Migrations e regression suite | Sim | Sim |

SQLite permanece opção local leve. O teste exclusivo PostgreSQL evita que
um CI verde apenas em SQLite seja confundido com garantia de comportamento
idêntico de lock transacional.

## Limitações

A instância PostgreSQL nativa em CI usa dados descartáveis de teste. Não confirma
performance sob carga, backup, disponibilidade, segurança de proxy/TLS ou
confiabilidade de bancos gerenciados. A execução das migrations na etapa
pré-teste não substitui um plano de rollback e migração em produção.
