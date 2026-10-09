# Histórico auditável — CHM-202

## Objetivo

Registrar no banco mudanças relevantes feitas nos chamados pela API e por edição no Django Admin, com contexto suficiente para atribuir autoria e reconstruir o estado anterior. Esse histórico não é um log de segurança universal; as limitações abaixo são parte do contrato atual.

## O que é registrado

A cada `PATCH` ou `PUT` aceito pelo endpoint de ticket, ou edição persistida no Django Admin, as alterações **efetivas** de `status`, `priority` e `assignee` são persistidas em `TicketAuditEvent`.

Cada evento registra:

- chamado vinculado, identificador e referência do chamado preservados em snapshot;
- campo modificado;
- valor anterior e novo valor (`""` representa responsável não atribuído);
- ator vinculado, nome do ator em snapshot e indicador de equipe;
- horário de criação.

As transições de `closed` continuam as regras do CHM-201: fechamento permitido a partir dos estados admitidos, reabertura de `closed` rejeitada. Tentativas rejeitadas **não** produzem eventos. Repetir o mesmo valor não produz evento.

O serviço `tickets/audit.py` prepara os eventos após validação do serializer ou formulário administrativo; uma transação engloba atualização e histórico. Em PostgreSQL, a seleção para update é bloqueada por `SELECT FOR UPDATE` antes da validação. A semântica de locks é dependente do banco (SQLite difere de PostgreSQL).

## Endpoint GET

`GET /api/tickets/{ticket_pk}/history/`

Retorno paginado usando o padrão DRF. Cada item possui:

- `id`
- `ticket_reference`
- `field`
- `old_value`
- `new_value`
- `actor_display`
- `created_at`

### Permissões

- Visitante anônimo: **401**.
- Solicitante de outro chamado: **404** (não revela existência).
- Solicitante dono do chamado: somente eventos de status e prioridade; identificação do ator mascarada como `Equipe de suporte` ou `Solicitante`.
- Staff: eventos completos (inclusive atribuição), com nome do ator original.

O endpoint é **somente leitura**. Dados de eventos não podem ser criados/editados via esta rota.

## Persistência após exclusão

Se o chamado for excluído, os eventos continuam no banco com `ticket = NULL`, referência e ID do chamado em snapshot. Excluir o ator também preserva seu nome em snapshot. Histórico de chamados excluídos **não** é consultável por esse endpoint; eventual consulta administrativa e política de retenção/anonimização precisam ser especificadas antes de produção.

## Limitações explícitas

- Esta implementação observa atualizações pela **API DRF e pelo formulário Django Admin de chamados**. Alterações diretas pelo ORM, `QuerySet.update` ou scripts externos **não** geram eventos automaticamente.
- O gerenciamento administrativo de comentários mantém operações independentes e não é coberto pela trilha `TicketAuditEvent`. Não declarar auditoria de comentários sem uma política específica.
- Criação de chamado, alteração de título/descrição, comentários, exclusão e tentativas de acesso negadas não geram eventos nesta etapa.
- Não há proteção contra alterações maliciosas por quem já possua privilégios administrativos de banco; "auditável" significa trilha persistente no aplicativo, não log imutável à prova de adulteração.
- Os registros históricos preservam nomes e identificadores: deverão integrar a futura política de privacidade e retenção.
- O CI atual executa SQLite e PostgreSQL 16; os cenários de auditoria e API são exercitados em ambos, mas não equivalem a testes de carga ou pentest.

## Testes

`tickets/tests/test_admin_lifecycle.py` cobre a edição administrativa; `tickets/tests/test_audit_history.py` cobre gravação, múltiplos campos, autor e horário, filtros de acesso, anonimização da equipe, endpoints somente leitura, rollback em falha, ausência de eventos em mudanças inválidas/idempotentes, integridade dos snapshots após exclusão e schema OpenAPI.
