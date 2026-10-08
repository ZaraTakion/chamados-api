# Status do Projeto

## Agora — Sprint 02: Domínio e consistência

- Sprint 00 e Sprint 01: **Done**.
- Sprint 02: **ativa**.
- [CHM-201 #5](https://github.com/ZaraTakion/chamados-api/issues/5): **Done**, PR #19 merged.
- [CHM-202 #6](https://github.com/ZaraTakion/chamados-api/issues/6): **Done**, PR #20 merged.
- [CHM-203 #7](https://github.com/ZaraTakion/chamados-api/issues/7): **Review**, aguardando validação local.
- Branch: `feat/chm-203-consistent-errors`.
- WIP: **1 tarefa Doing**.

## Evidências concluídas

### CHM-201
- Regras de transição centralizadas.
- 35 testes, CI verde em Python 3.10–3.12.
- Coverage: 93,2% CI / 94,1% Windows.

### CHM-202
- Modelo e migration de trilha auditável, endpoint protegido, persistência atômica e testes de integridade.
- 48 testes verdes em Python 3.10–3.12.
- Coverage: 94,4% CI / 95,1% Windows.
- Migration `tickets.0002_ticketauditevent` aplicada no Windows.
- PR #20 integrada à `main` após aprovação local.

## CHM-203 — Próxima entrega

Padronizar representação das exceções tratadas pelo Django REST Framework, diferenciando autenticação, autorização, validação e regras de negócio. Preservar códigos HTTP e campos de validação legados nesta etapa; adicionar contrato `error` estável e documentado.

## CHM-203 — Validação automatizada

- Handler central de exceções DRF em `chamados_api/errors.py`.
- Contrato aditivo `error: {code, message, details}`; códigos HTTP e campos anteriores preservados.
- Códigos específicos de autenticação, autorização, validação, regra de negócio, 404, 405, JSON inválido e throttling.
- Documentação e exemplos em `docs/API_ERRORS.md`.
- **62 testes aprovados por versão** em Python 3.10, 3.11 e 3.12.
- Ruff, Django check e migrations check: verdes.
- Coverage da aplicação: **94,8%** (389 statements, 16 misses, 88 branches, 7 partial branches).

[PR #21](https://github.com/ZaraTakion/chamados-api/pull/21) em draft até validação local no Windows.

**Review pendente:** repetir checks e testes no Windows; não iniciar CHM-301 antes do fechamento da Sprint 02.
