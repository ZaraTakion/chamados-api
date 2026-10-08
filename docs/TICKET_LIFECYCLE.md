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
- `tickets/tests/test_transitions.py` verifica todas as combinações (origem, destino) e os fluxos de API.

## Limitações e próximos passos

Esta etapa valida **atualizações feitas pelos endpoints DRF**. Não é um bloqueio no banco de dados e não intercepta `QuerySet.update()`, Django Admin nem manipulações diretas do modelo.

Criação de tickets mantém o contrato anterior: solicitantes não recebem autorização para escolher status, enquanto a equipe pode criar tickets com status explícito conforme o serializer atual. Padronizar regras de estado inicial é uma decisão separada; não foi introduzida implicitamente neste CHM.

Histórico auditável, mudanças concorrentes e registro de ator/data são responsabilidade dos próximos itens do roadmap (especialmente CHM-202).
