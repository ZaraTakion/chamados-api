# Status do Projeto

## Agora — Sprint 06: Deploy e release profissional

- Sprints 00, 01, 02, 03, 04 e 05: **Done**.
- [CHM-301 #8](https://github.com/ZaraTakion/chamados-api/issues/8): **Done**, PR #22 merged.
- [CHM-302 #9](https://github.com/ZaraTakion/chamados-api/issues/9): **Done**, PR #23 merged, validação Windows aprovada.
- [CHM-401 #10](https://github.com/ZaraTakion/chamados-api/issues/10): **Done** — PR #24 integrada à main; QA Windows e CI aprovados.
- [CHM-402 #11](https://github.com/ZaraTakion/chamados-api/issues/11): Done, PR #25 merged; 95 testes aprovados e 1 skip no Windows, 94,5% coverage.
- [CHM-403 #12](https://github.com/ZaraTakion/chamados-api/issues/12): **Done** — PR #26 integrada, migrations e readiness smoke verificados no PostgreSQL CI.
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
- Sprint 05 encerrada. WIP: [CHM-601 #15](https://github.com/ZaraTakion/chamados-api/issues/15) é o único item Doing. Preparação técnica foi integrada via PR #29; implantação real ainda não realizada.

## CHM-401 — Observabilidade

- [PR #24 integrada via squash merge](https://github.com/ZaraTakion/chamados-api/pull/24), commit `ef5e57f`.
- Identificação de requisição e logging HTTP em JSON.
- Testes de correlação e formatação segura adicionados.
- Documentação em [OBSERVABILITY.md](./OBSERVABILITY.md).
- CI: Python 3.10–3.12 (SQLite) e PostgreSQL 16 aprovados; 82 testes descobertos por ambiente (SQLite: 81 passaram e 1 skip; PostgreSQL: 82 passaram). Coverage no CI 94,3%.
- Windows: Ruff, check e migrations verdes; 82 testes (81 passaram, 1 skip PostgreSQL), 286.338s, cobertura **94,8%** (457 statements, 18 misses, 104 branches, 11 partial branches).
- Logs JSON observados durante os testes de erro, com request ID e sem informação sensível nas linhas exibidas.

## CHM-402 — Aceite concluído

- Endpoints `/api/health/live/` e `/api/health/ready/`, mantendo `/api/health/` como liveness legado.
- Readiness executa `SELECT 1` e devolve 503 seguro se o banco estiver indisponível.
- Guarda de inicialização de produção: segredo aleatório forte, hosts explícitos, PostgreSQL persistente e HTTPS.
- Checklist de deploy em [PRODUCTION_SECURITY.md](./PRODUCTION_SECURITY.md).
- CI aprovado em Python 3.10–3.12/SQLite e PostgreSQL 16: 96 testes descobertos por ambiente.
- QA Windows: 95 testes passaram, 1 skip específico PostgreSQL, 0 falhas, 285.633s; cobertura 94,5%.
- PR #25 squash merged na main em 08/10/2026, commit e9a9571c.
- CHM-403 concluída com a PR #26; Sprint 04 encerrada.

## CHM-403 — Evidência de PostgreSQL no CI

- PostgreSQL 16 já executava toda a suíte desde CHM-302.
- Esta entrega explicita `migrate --noinput`, `migrate --check` e smoke test de `/api/health/ready/` antes dos testes.
- SQLite permanece na matriz 3.10–3.12 e as diferenças estão descritas em [CI_POSTGRESQL.md](./CI_POSTGRESQL.md).
- CI completo: 4/4 jobs verdes, 96 testes por ambiente, 1 skip somente em SQLite; 94,0% coverage. PostgreSQL 16 aprovou migrations explícitas, conferência e smoke test.
- [PR #26 integrada](https://github.com/ZaraTakion/chamados-api/pull/26), commit `b2108028`; Issue #12 fechada.

## Encerramento Sprint 04 — 08/10/2026

- CHM-401, CHM-402 e CHM-403 Done, com PRs #24, #25, #26 integradas.
- Review: observabilidade segura, health probes e configuração de produção, PostgreSQL 16 real no CI.
- Retrospectiva: preservar contratos anteriores (throttling legado); detectar regressões no CI; confirmar Windows antes dos merges de código.
- Sprint 05 concluída via PRs #27 e #28. Sprint 06 iniciada com CHM-601; CHM-602 aguarda deploy real validado.

## CHM-501 — Redis + Celery (Done)

- Broker Redis e result backend parametrizados via ambiente.
- Worker separado em Docker Compose, concorrência 1 e Redis sem porta publicada.
- Tarefa `tickets.queue_summary` é read-only e retorna apenas contagens por status, sem PII.
- Retries em falha transitória de banco e timeouts limitados; testes eager sem exigir Redis.
- Implementação documentada em [ASYNC_ARCHITECTURE.md](./ASYNC_ARCHITECTURE.md).
- CI: 5/5 jobs aprovados, incluindo Redis+Celery real em Docker Compose e PostgreSQL 16; 101 testes descobertos por ambiente e 94,3% de cobertura.
- QA Windows em 08/10/2026: 101 testes encontrados, 100 passaram, 1 skip PostgreSQL, 0 falhas, 288.867s; coverage **94,7%** (527 statements, 21 misses, 118 branches, 11 partial branches); Ruff, Django e migrações verdes.
- [PR #27 integrada](https://github.com/ZaraTakion/chamados-api/pull/27), commit `49b549bc87c348f9bdf445cc36710902ee0d3e60`; Issue #13 fechada.
- CHM-502 entregue: notificações internas por outbox transacional, inbox privada e Celery Beat; PR #28 integrada.

## CHM-502 — Notificações assíncronas (Done)

- Eventos: criação, atribuição, status, resolução e comentário público, sem vazamento de notas internas.
- Caixa de entrada privada no `GET /api/notifications/`.
- Outbox transacional no banco e processamento agendado pelo Celery Beat; nenhuma conexão Redis no caminho HTTP.
- Migration `0004_notifications`, testes de rollback/idempotência/privacidade, CI real Redis+worker+scheduler.
- [NOTIFICATIONS.md](./NOTIFICATIONS.md): implementação e segurança documentadas.
- CI: 5/5 jobs verdes; 113 testes por ambiente (SQLite: 112 passaram, 1 skip; PostgreSQL: 113 passaram), 94,8% cobertura.
- Windows: 113 testes (112 passaram, 1 skip), 0 falhas em 286.077s; cobertura **95,2%**; Ruff/Django/migrations check aprovados.
- Backup SQLite `db-backup-chm502-1791505810.sqlite3` íntegro; migration `tickets.0004_notifications` aplicada; `showmigrations`: 0001–0004 `[X]`.
- [PR #28 integrada](https://github.com/ZaraTakion/chamados-api/pull/28), commit `29b06109`. Issue #14 concluída.

## Encerramento Sprint 05 — 08/10/2026

- CHM-501 e CHM-502 **Done**, com PRs #27 e #28 integradas.
- Review: Redis/Celery em Compose com testes reais e outbox transacional com caixa de entrada privada; falhas do broker não bloqueiam a escrita HTTP.
- Retrospectiva: manter evidência do worker real no CI, evitar efeitos colaterais em transações HTTP, validar backup antes de migrações locais.
- Próximo: CHM-601 (#15) — hospedagem PostgreSQL persistente, HTTPS, worker + scheduler, logs, rollback e runbook. Sem deploy em produção confirmado até agora.

## CHM-601 — Preparação técnica integrada; deploy real pendente (Doing)

- Railway Infrastructure as Code (`.railway/railway.ts`): Web/Worker/Beat, Postgres e Redis privados, healthcheck de readiness e migrations de pre-deploy. O antigo Config as Code, incompatível com serviços novos, foi retirado.
- Docker context reforçado: `.env.*`, dados, backups e artefatos locais excluídos da imagem.
- Smoke HTTP público e offline unit tests, além de validação end-to-end no Docker CI.
- Runbooks: [DEPLOY_RAILWAY.md](./DEPLOY_RAILWAY.md) e [OPERATIONS_RUNBOOK.md](./OPERATIONS_RUNBOOK.md).
- **CI final:** 6/6 jobs verdes (SQLite 120 testes passaram + 1 skip; PostgreSQL 121 aprovados), cobertura 94,1%; Railway IaC typecheck e Docker HTTP/Celery smoke aprovados.
- **QA Windows:** Ruff, Django check, migrations check aprovados; 121 testes descobertos, 120 passaram + 1 skip, 0 falhas em 261.486s; cobertura **94,5%**.
- **Código integrado:** [PR #29](https://github.com/ZaraTakion/chamados-api/pull/29) squash merged em `23fbaad2`, sem criar recursos na nuvem.
- **Pendências CHM-601:** aprovar recursos/custos, provisionar projeto Railway separado, verificar PostgreSQL persistente e backups, Redis privado, HTTPS real, migrações, logs, Worker/Beat, smoke autenticado com dados sintéticos, recuperação e rollback. Issue #15 continua **aberta**; nenhuma produção publicada declarada.

## Demonstração local sem custos — Done (PR #30)

- Decisão do usuário: **não autorizar recursos pagos** no Railway ou outro
  provedor. Nenhuma infraestrutura externa deve ser criada ou cobrada.
- Nova subentrega CHM-601 na branch `feat/chm-601-zero-cost-local-demo`:
  comando Django `process_notifications` para processar outbox local sem
  Redis/Celery worker, em processo separado do servidor HTTP.
- API continua no SQLite local e as notificações são registradas na inbox
  autenticada; comandos e limitações em [LOCAL_DEMO.md](./LOCAL_DEMO.md).
- **CI:** [6/6 jobs aprovados](https://github.com/ZaraTakion/chamados-api/actions/runs/37873992540), 128 testes descobertos por ambiente (SQLite 127 aprovações + 1 skip; PostgreSQL 128 aprovados), cobertura 94,2%; inclui teste E2E com JWT real e inbox privada, Docker e IaC.
- **QA Windows:** Ruff e Django check verdes, 6/6 testes locais em 0,403s; Swagger HTTP 200, registro HTTP 201, login JWT HTTP 200, criação de `CH-000001` HTTP 201, outbox real 1 evento/1 processado/1 notificação.
- **Leitura da inbox autenticada:** confirmada no teste E2E automatizado com contas fictícias, **não** diretamente no navegador do proprietário.
- [PR #30 integrada](https://github.com/ZaraTakion/chamados-api/pull/30), commit `6585d2a`. Nenhum serviço externo provisionado.
- CHM-601 (deploy original de produção) permanece aberta, sem custo autorizado; CHM-602 (release e portfólio) aguarda decisão de escopo para versão local.

## CHM-602 — Pré-release local v1.0.0-local.1 (Done)

- Coleção Postman (18 requisições), case para recrutadores, arquitetura, changelog e evidências sanitizadas integradas via PR #31.
- Captura **real** do Swagger gerada em Chrome headless no CI e [anexada à GitHub Release](https://github.com/ZaraTakion/chamados-api/releases/download/v1.0.0-local.1/swagger-real-ci.png).
- [GitHub Release `v1.0.0-local.1` publicada](https://github.com/ZaraTakion/chamados-api/releases/tag/v1.0.0-local.1) após 7 jobs bem-sucedidos (6 verificações + publicação). Tag aponta para `5edb6d8`.
- Checklist em [RELEASE_CHECKLIST.md](./RELEASE_CHECKLIST.md).
- **Não existe:** produção HTTPS, serviço gerenciado, backup/rollback de
  produção ou URL pública. CHM-601 #15 fica aberta e bloqueada; não
  contratar nada sem autorização.

### Encerramento técnico CHM-602 — 09/10/2026

- [PR #31 merged](https://github.com/ZaraTakion/chamados-api/pull/31), CI de PR 6/6 verde. 
- [Execução da release](https://github.com/ZaraTakion/chamados-api/actions/runs/37879361318): 7 jobs aprovados, PostgreSQL 133/133, SQLite 132 pass + 1 skip, cobertura 94,2%; screenshot Swagger como artefato e asset de release (74.540 bytes).
- Reprodutibilidade: coleção Postman sem credenciais, guias, case e CHANGELOG.
- **Escopo local Done; deploy original de produção CHM-601 continua bloqueado/aberto**, sem domínio público ou recursos faturáveis.

## CHM-601 — Preview privado e gratuito (código Done; ativação remota pendente)

- Retomada da CHM-601 para preparar **preview temporário com acesso
  protegido por email**, sem hospedagem paga e sem reutilizar o banco
  do usuário. Nenhum recurso externo foi contratado.
- [PR #32 integrada](https://github.com/ZaraTakion/chamados-api/pull/32), commit `9444dfaf`.
- Cloudflare Quick Tunnel exige `--allowed-mail` e versão mínima
  `2026.9.3`; modo anônimo sem e-mail permitido é recusado.
- Servidor local Waitress no loopback, Django `DEBUG=false`, segredo
  de sessão efêmero, `ALLOWED_HOSTS` exato e banco SQLite isolado.
- [CI #37948905306](https://github.com/ZaraTakion/chamados-api/actions/runs/37948905306): **6/6 jobs verdes**, PostgreSQL **143/143 testes aprovados**, SQLite **142 aprovados + 1 skip**, cobertura 93,7%; smoke Waitress/HTTPS/Host no loopback, Docker/Redis/Celery e Railway IaC aprovados.
- Testes e [guia](./PROTECTED_TUNNEL.md) entregues. Falta somente a **ativação e verificação externa** do túnel protegido no Windows do proprietário, que não pode ser feita via GitHub.
- CHM-601 **não** será marcada Done como produção: sem disponibilidade
  24/7, banco remoto/backup, monitoramento real nem domínio permanente.
