# Status do Projeto

## Agora — Sprint 02: Domínio e consistência

- **Sprint 00:** Done
- **Sprint 01 — Qualidade e baseline:** Done
- **Sprint ativa:** Sprint 02 — Domínio e consistência
- **Review atual:** [CHM-201 #5](https://github.com/ZaraTakion/chamados-api/issues/5) — CI verde; teste local pendente
- **Branch:** `feat/chm-201-ticket-transitions`
- **Backlog:** CHM-202, CHM-203 e as sprints seguintes
- **WIP:** no máximo 1 item Doing

## Evidências da Sprint 01

- [CHM-101 #3](https://github.com/ZaraTakion/chamados-api/issues/3): Done — Ruff, Coverage, CI e baseline.
- [CHM-102 #4](https://github.com/ZaraTakion/chamados-api/issues/4): Done — regressão de autenticação, permissões, tickets, comentários, filtros, paginação e OpenAPI.
- Suíte de testes: **7 → 25 testes**.
- CI: **Python 3.10, 3.11 e 3.12** com sucesso.
- Cobertura atual de código da aplicação: **92,7% no CI** e **93,7% no Windows 10 / Python 3.12**.
- Ruff, check e migrations: verdes.
- Schema OpenAPI sem os warnings de serializer anteriormente vistos.

**Nota:** O CHM-102 excluiu arquivos de teste do cálculo de Coverage. Os percentuais das duas tarefas não têm exatamente o mesmo denominador.

## Sprint Review e Retrospectiva 01

**Entregas demonstráveis:** PR #17 (baseline) e PR #18 (matriz de testes), ambas merged após validação no CI e no Windows.

**Manter:** uma tarefa Doing por vez, revisão via PR e validação de Windows antes do merge.

**Melhorar:** registrar regras de domínio explicitamente antes da implementação e testar transições válidas e inválidas.

**Evitar:** adicionar tecnologia que não seja necessária e inflar cobertura incluindo arquivos de testes.

## Sprint Goal 02

Centralizar regras de domínio, tornar transições de chamado explícitas, preparar o histórico auditável e padronizar respostas de erro sem quebrar os contratos existentes.

### CHM-201 — Foco atual

- Definir a matriz de mudanças de status.
- Validar transições em um módulo de domínio testável.
- Manter regras de autorização existentes: somente staff altera status.
- Testar mudanças permitidas, inválidas, idempotentes e término em `closed`.
- Validar CI e, depois, Windows local antes do merge.

### Validação automatizada do CHM-201

- 35 testes verdes por versão no CI: Python 3.10, 3.11 e 3.12;
- Ruff, Django check e migrations check verdes;
- cobertura de código da aplicação: **93,2%**;
- matriz dos 25 pares de status exercitada por subtestes;
- validação por endpoint e autorização de staff cobertas;
- cache de throttling reinicializado entre testes sem desativar o rate limit.

A [PR #19](https://github.com/ZaraTakion/chamados-api/pull/19) está em draft e aguarda validação local no Windows.

Não iniciar CHM-202 até CHM-201 estar Done.
