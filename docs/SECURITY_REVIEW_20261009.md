# Revisão técnica complementar — 2026-10-09

Esta revisão registra **evidência observável no código** e evita criar novas abstrações onde os controles existentes já atendem ao escopo. Não equivale a pentest ou auditoria externa.

## Arquitetura e controles examinados

| Área | Evidência no repositório | Resultado |
|---|---|---|
| Isolamento de chamados | `tickets/views.py:TicketViewSet.get_queryset()` restringe solicitantes ao próprio `requester`; equipe vê fila global | Controle presente; manter testes de IDOR |
| Comentários internos | `TicketCommentListCreateView.get_queryset()` filtra `is_internal=False` fora da equipe | Controle presente |
| Histórico de alterações | `TicketAuditHistoryView.get_queryset()` restringe campos mostrados ao solicitante | Controle presente |
| Notificações | `TicketNotificationListView.get_queryset()` restringe inbox ao `recipient` autenticado | Controle presente |
| Persistência auditável | `TicketViewSet.update()` usa `transaction.atomic`, com gravação de eventos e outbox transacional | Controle presente |
| Broker indisponível | `tickets/notifications.py` grava intenções na outbox sem acesso ao Redis durante requisição HTTP | Desacoplamento presente |
| Revogação de equipe | `tickets/notifications.py` verifica se o responsável continua ativo e equipe antes de gerar novos avisos | Corrigido nesta branch; coberto por regressões |
| Django Admin | `tickets/admin.py` valida transições e audita mudanças de tickets | Corrigido nesta branch; preserva o status inicial explícito para equipe |
| Implantação | `chamados_api/settings.py` separa desenvolvimento, preview protegido e produção, exige segredo e configuração de banco/hosts | Controles de inicialização presentes |
| CI | [GitHub Actions](https://github.com/ZaraTakion/chamados-api/actions) com jobs Python, PostgreSQL e Compose descritos no histórico | Validar execução por commit antes de divulgar números |

## Riscos e limites que permanecem

1. **Exclusão de chamados por equipe:** `TicketViewSet.perform_destroy()` permite a exclusão física; dependendo das políticas de retenção da organização, isso pode eliminar registros históricos associados. Não alterar o contrato DELETE sem decisão de produto, política de retenção e teste de migração.
2. **Rate limiting:** throttling DRF oferece proteção básica e pode depender do cache empregado; uma arquitetura com múltiplas réplicas necessita verificação de backend de cache compartilhado e controles no edge.
3. **Produção não provisionada:** há pré-release local verificável, não evidência de serviço HTTPS público, política de backup remoto ou operação 24/7.
4. **Comentário administrativo:** a interface administrativa permite operações sobre comentários fora do fluxo da API; estas alterações não estão cobertas por `TicketAuditEvent` e exigem política de moderação/auditoria antes de operação regulada.
5. **Privacidade de demonstrações:** usar somente dados sintéticos e contas descartáveis; não incluir tokens reais no Postman, artefatos, issues ou screenshots.

## Evidências e release

- [Pré-release local `v1.0.0-local.1`](https://github.com/ZaraTakion/chamados-api/releases/tag/v1.0.0-local.1).
- [Case técnico existente](./PORTFOLIO.md), [runbook](./OPERATIONS_RUNBOOK.md) e [teste de autorização de notificações](../tickets/tests/test_notifications.py).
- [Run CI aprovada observado durante revisão](https://github.com/ZaraTakion/chamados-api/actions/runs/37949540437). Resultados dessa execução não devem ser confundidos com execução local nova.

**Conclusão desta revisão:** as rotas públicas, o esquema persistido e a criação de chamados com status explícito pela equipe permanecem compatíveis. Foram adicionadas validações e auditoria no Django Admin, filtragem de novos avisos a antigos responsáveis sem acesso e testes de regressão. Os riscos de retenção, comentários administrativos e deploy ainda exigem decisões próprias.
