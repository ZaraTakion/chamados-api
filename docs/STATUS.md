# Status do Projeto

## Agora — Sprint 04: Produção e observabilidade

- Sprints 00, 01, 02 e 03: **Done**.
- [CHM-301 #8](https://github.com/ZaraTakion/chamados-api/issues/8): **Done**, PR #22 merged.
- [CHM-302 #9](https://github.com/ZaraTakion/chamados-api/issues/9): **Done**, PR #23 merged, validação Windows aprovada.
- [CHM-401 #10](https://github.com/ZaraTakion/chamados-api/issues/10): **Done** — PR #24 integrada à main; QA Windows e CI aprovados.
- [CHM-402 #11](https://github.com/ZaraTakion/chamados-api/issues/11): Done, PR #25 merged; 95 testes aprovados e 1 skip no Windows, 94,5% coverage.
- [CHM-403 #12](https://github.com/ZaraTakion/chamados-api/issues/12): Doing — migrations explícitas e smoke test em PostgreSQL 16 CI.
- WIP limit: uma tarefa Doing por vez.

## CHM-301 — Evidências concluídas

- Testes de regressão contra N+1 para listagem e detalhe de chamados, comentários e histórico.
- Contagens de consultas iguais com 1 e 20 registros: listagem 3, detalhe 2, comentários 4, histórico 4.
- Sem JOIN: 21 consultas para 20 objetos; com `select_related`: 1 consulta (tickets e comentários).
- Nenhuma alteração de código de produção foi necessária: `select_related` já estava implementado corretamente.
- CI Python 3.10, 3.11 e 3.12 verde, **70 testes**, **95,2% de cobertura**.
- Windows/Python 3.12: **70/70 testes** em 245.393s, Ruff/check/migrations verdes, **95,8% de cobertura local**.
- [Relatório de baseline e limites da medição](./ORM_QUERY_BASELINE.md).
- PR #22: squash merge concluído.

## CHM-302 — Entrega concluída

Foram revisados índices, adicionadas constraints e corrigido o bloqueio de linha para PostgreSQL, com testes de integridade nas duas engines. Nenhum ganho de latência foi alegado sem medição.

### Critérios de aceitação verificados

1. Mapear os índices existentes (implícitos e explícitos), filtros e ordenações.
2. Selecionar índices apenas com justificativa documentada.
3. Garantir invariantes relevantes do domínio no banco, com testes.
4. Revisar operações que exigem atomicidade e testar rollback.
5. Fazer verificação real em PostgreSQL; não usar SQLite como prova substituta.
6. Validar CI, migrations e Windows antes de merge.

CHM-301 e CHM-302 estão encerrados. Sprint 03 concluída em 08/10/2026; Sprint 04 está ativa; CHM-401 concluída.

## CHM-302 — Resultados da validação

- Migration `0003_database_integrity`: restrições de domínio para status, prioridade e tipo de evento.
- `select_for_update(of=("self",))`: lock somente da linha do ticket, compatível com `assignee` anulável.
- CI: 75 testes verdes em Python 3.10–3.12 (SQLite), um teste específico PostgreSQL é pulado nesses ambientes.
- PostgreSQL 16 real no GitHub Actions: **75 testes aprovados**, incluindo cenário de lock com responsável nulo.
- Ruff, Django check, migrations check verdes.
- Coverage da aplicação: **95,2%**.
- Índices atuais revisados; nenhum composto novo adicionado sem comprovação de ganho.
- Documento de decisões: [DATABASE_INTEGRITY.md](./DATABASE_INTEGRITY.md).
- Windows/SQLite: backup local concluído antes da migration; `tickets.0003_database_integrity` aplicada com sucesso.
- Windows: Ruff/check/migrations verdes; suíte encontrou **75 testes**, **74 aprovados e 1 skip específico PostgreSQL**, em **259.988s**; **95,8% de cobertura** (391 statements, 13 misses, 88 branches, 7 partial branches).
- PR #23: [squash merge concluído](https://github.com/ZaraTakion/chamados-api/pull/23) (commit `10c08a9`). Issue #9 fechada.

## Sprint 04 — CHM-401 concluída

- Middleware gera request ID aleatório de 32 caracteres para cada requisição.
- Header de resposta `X-Request-ID`, incluindo respostas com erro.
- Logs HTTP em JSON com campos seguros e sem corpos/credenciais/query strings.
- Nível configurável por `APP_LOG_LEVEL`; configurações locais/produção em [OBSERVABILITY.md](./OBSERVABILITY.md).
- Testes de segurança e correlação aprovados no CI e no Windows.
- WIP: CHM-402 é o único Doing da Sprint 04.

## CHM-401 — Observabilidade

- [PR #24 integrada via squash merge](https://github.com/ZaraTakion/chamados-api/pull/24), commit `ef5e57f`.
- Identificação de requisição e logging HTTP em JSON.
- Testes de correlação e formatação segura adicionados.
- Documentação em [OBSERVABILITY.md](./OBSERVABILITY.md).
- CI: Python 3.10–3.12 (SQLite) e PostgreSQL 16 aprovados; 82 testes descobertos por ambiente (SQLite: 81 passaram e 1 skip; PostgreSQL: 82 passaram). Coverage no CI 94,3%.
- Windows: Ruff, check e migrations verdes; 82 testes (81 passaram, 1 skip PostgreSQL), 286.338s, cobertura **94,8%** (457 statements, 18 misses, 104 branches, 11 partial branches).
- Logs JSON observados durante os testes de erro, com request ID e sem informação sensível nas linhas exibidas.

## CHM-402 — Preparação para Review

- Endpoints `/api/health/live/` e `/api/health/ready/`, mantendo `/api/health/` como liveness legado.
- Readiness executa `SELECT 1` e devolve 503 seguro se o banco estiver indisponível.
- Guarda de inicialização de produção: segredo aleatório forte, hosts explícitos, PostgreSQL persistente e HTTPS.
- Checklist de deploy em [PRODUCTION_SECURITY.md](./PRODUCTION_SECURITY.md).
- CI aprovado em Python 3.10–3.12/SQLite e PostgreSQL 16: 96 testes descobertos por ambiente.
- QA Windows: 95 testes passaram, 1 skip específico PostgreSQL, 0 falhas, 285.633s; cobertura 94,5%.
- PR #25 squash merged na main em 08/10/2026, commit e9a9571c.
- CHM-403 é o único item Doing.

## CHM-403 — Evidência de PostgreSQL no CI

- PostgreSQL 16 já executava toda a suíte desde CHM-302.
- Esta entrega explicita `migrate --noinput`, `migrate --check` e smoke test de `/api/health/ready/` antes dos testes.
- SQLite permanece na matriz 3.10–3.12 e as diferenças estão descritas em [CI_POSTGRESQL.md](./CI_POSTGRESQL.md).
- CI da nova mudança e review ainda pendentes.
