# Status do Projeto

## Agora — Sprint 02: Domínio e consistência

- Sprint 00: **Done**
- Sprint 01 — Qualidade e baseline: **Done**
- Sprint ativa: **Sprint 02 — Domínio e consistência**
- [CHM-201 #5](https://github.com/ZaraTakion/chamados-api/issues/5): **Done**, PR #19 merged
- [CHM-202 #6](https://github.com/ZaraTakion/chamados-api/issues/6): **Review — CI verde, teste local pendente**
- Branch ativa: `feat/chm-202-ticket-audit-history`
- Próximos itens: CHM-203 e sprints posteriores no Backlog
- Limite WIP: **1 item Doing**

## Resultados verificados

### Sprint 01
- Ruff + Coverage + CI em Python 3.10–3.12.
- Regressão ampliada de 7 para 25 testes.
- Cobertura da aplicação: 92,7% CI / 93,7% Windows (CHM-102).

### CHM-201 (Sprint 02)
- Matriz de transições em `tickets/transitions.py` e documentação em `docs/TICKET_LIFECYCLE.md`.
- 35 testes aprovados em Python 3.10, 3.11 e 3.12.
- Ruff/check/migrations aprovados.
- Cobertura da aplicação: **93,2% CI / 94,1% Windows 10, Python 3.12**.
- PR #19 mergeada após teste local.

## Próximo objetivo — CHM-202

Implementar histórico auditável persistente para mudanças de status, prioridade e atribuição.

- Registrar valores anteriores e novos, ator e horário.
- Gravar alterações relevantes de forma transacional e coerente com as permissões atuais.
- Staff visualiza histórico completo; solicitante vê apenas eventos explicitamente permitidos do próprio chamado.
- Impedir vazamento de informações internas e de chamados alheios.
- Testar ações autorizadas, não autorizadas e ausência de registros em operações inválidas.
- Atualizar API/OpenAPI e documentação.
- Validar no CI e no Windows antes do merge.

## CHM-202 — Validação automatizada

- Migration `0002_ticketauditevent` validada.
- 48 testes aprovados por versão em Python 3.10, 3.11 e 3.12.
- Ruff, Django system check e migrations check verdes.
- Cobertura da aplicação no CI: **94,4%**.
- Contrato de histórico e suas limitações em [TICKET_AUDIT.md](./TICKET_AUDIT.md).
- [PR #20](https://github.com/ZaraTakion/chamados-api/pull/20) em draft: aguardando testes no Windows.

## Critério para merge

Repetir checks e 48 testes no Windows; executar `python manage.py migrate` para aplicar a nova tabela no SQLite local após aprovação. Não iniciar CHM-203 até CHM-202 estar Done.
