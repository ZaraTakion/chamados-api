# Status do Projeto

## Agora — Sprint 03: Banco e performance

- Sprint 00: **Done**
- Sprint 01 — Qualidade e baseline: **Done**
- Sprint 02 — Domínio e consistência: **Done**
- Sprint ativa: **Sprint 03 — Banco e performance**
- **Doing:** [CHM-301 #8](https://github.com/ZaraTakion/chamados-api/issues/8)
- Branch de desenvolvimento: `perf/chm-301-orm-query-baseline`
- CHM-302 permanece em Backlog, com limite WIP de uma tarefa em Doing.

## Sprint 02 — Entregas e evidências

- [CHM-201 #5](https://github.com/ZaraTakion/chamados-api/issues/5): regras explícitas de transição, PR #19 merged; 35 testes e 94,1% de cobertura local.
- [CHM-202 #6](https://github.com/ZaraTakion/chamados-api/issues/6): trilha auditável com migração, PR #20 merged; 48 testes e 95,1% de cobertura local.
- [CHM-203 #7](https://github.com/ZaraTakion/chamados-api/issues/7): contrato de erros compatível, PR #21 merged; **62 testes aprovados** em Python 3.10, 3.11 e 3.12 no CI, **94,8% de cobertura CI**.
- Aceite local do CHM-203: Windows, Python 3.12, Ruff e Django check verdes, nenhuma migration pendente, **62/62 testes aprovados** (221.716s), **95,4% de cobertura local**.
- Documentação: `docs/TICKET_LIFECYCLE.md`, `docs/TICKET_AUDIT.md` e `docs/API_ERRORS.md`.

## Sprint 03 — Objetivo

Medir, explicar e melhorar o comportamento de acesso a dados no ORM e PostgreSQL.

### CHM-301 — Primeiro item

1. Medir **listagem**, **detalhe** e **comentários** dos tickets em cenários requester/staff, com poucos e muitos registros.
2. Registrar valores reais de query count antes de propor otimização (baseline).
3. Detectar possíveis N+1 e revisar `select_related`/`prefetch_related` onde necessário.
4. Aplicar otimizações apenas quando houver justificativa mensurável.
5. Criar testes de regressão e documentar comparação antes/depois.
6. Revalidar Ruff, check, migrations, testes e cobertura no CI Python 3.10–3.12; obter aceite local antes do merge.

A otimização de transações/índices é CHM-302; não iniciar antes de CHM-301 Done.
