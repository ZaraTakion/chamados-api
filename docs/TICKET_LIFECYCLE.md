# Ciclo de vida dos chamados — CHM-201

## Estados

A API mantém os estados armazenados no modelo `Ticket.Status`:

- `open`: aberto;
- `in_progress`: em atendimento;
- `waiting`: aguardando solicitante;
- `resolved`: resolvido;
- `closed`: fechado.

## Matriz de transições em atualizações

| Estado atual | Próximos estados permitidos |
| --- | --- |
| `open` | `in_progress`, `closed` |
| `in_progress` | `waiting`, `resolved`, `closed` |
| `waiting` | `in_progress`, `resolved`, `closed` |
| `resolved` | `in_progress`, `closed` |
| `closed` | nenhum (terminal) |

Reaplicar o status atual não é uma transição e é aceito (idempotência da intenção).
`resolved → in_progress` permite retomar atendimento após resolução.
`open → closed` permite fechamento direto pela equipe.

## Permissões e erros

- Apenas usuários `is_staff` podem mudar o status, inclusive para o mesmo valor.
- Solicitantes podem editar campos permitidos, mas alterações de `status` retornam **HTTP 400**, conforme contrato existente do serializer.
- Transições inválidas retornam **HTTP 400**, com detalhe no campo `status`.
- Um chamado `closed` não pode voltar a estados anteriores.
- Editar outros campos de um chamado fechado mantém o comportamento anterior.
- Um status desconhecido é rejeitado pelo domínio (e um valor inválido recebido via API também é rejeitado pelo ChoiceField do DRF).

## Onde mora a regra

- `tickets/transitions.py` contém a matriz e `validate_ticket_transition`; não importa views nem serializers.
- `tickets/serializers.py` usa a regra na atualização de status.
- `tickets/admin.py` reutiliza a mesma regra nos formulários de edição do Django Admin.
- `tickets/tests/test_transitions.py` e `tickets/tests/test_admin_lifecycle.py` verificam os fluxos da API e do Admin.

## Limitações e próximos passos

A API e o formulário de edição no Django Admin validam transições; **não há bloqueio de máquina de estados diretamente no banco**. Scripts, `QuerySet.update()` e operações ORM diretas podem contornar o domínio e não devem ser usados para mudanças operacionais sem uma auditoria explícita.

**Compatibilidade preservada:** solicitantes não podem escolher o status inicial; equipe pode criar tickets com status explícito no contrato atual, inclusive na criação administrativa. Esta revisão não alterou esse comportamento existente.

O Django Admin agora registra as mudanças efetivas de status, prioridade e responsável no mesmo modelo de auditoria e gera eventos de outbox no mesmo fluxo de gravação. O responsável precisa ser um usuário da equipe ativa.

Validação em PostgreSQL/SQLite usa estratégias de bloqueio diferentes; concorrência e políticas de retenção de chamados devem ser consideradas antes de deploy.
