# CHM-301 — Baseline de consultas ORM e prevenção de N+1

## Objetivo e método

Medir o número de consultas SQL executadas pelos endpoints críticos da Chamados API e proteger o projeto de regressões N+1.

As medições foram realizadas no SQLite do GitHub Actions em **08/10/2026**, com Python **3.10, 3.11 e 3.12**. Todas as três execuções produziram os mesmos resultados. Os testes estão em `tickets/tests/test_query_performance.py` e utilizam `CaptureQueriesContext(connection)`.

Cada requisição é executada com o token JWT já obtido antes de abrir o contexto de captura. A contagem **inclui** o processamento HTTP/DRF, autenticação durante a requisição, autorização e consultas de paginação, mas **exclui** preparação dos dados de teste e obtenção inicial do token.

Os cenários usam um chamado ou vinte chamados no endpoint de listagem, um ou vinte comentários públicos (autores alternados entre usuários) e um ou vinte eventos auditáveis. Para detalhe, o mesmo chamado é consultado com um ou vinte chamados totais no banco. A paginação padrão exibe até vinte resultados.

## Contagem por endpoint

| Endpoint e papel | Com 1 registro | Com 20 registros | Crescimento |
| --- | ---: | ---: | ---: |
| `GET /api/tickets/` — staff | 3 | 3 | 0 |
| `GET /api/tickets/` — requester | 3 | 3 | 0 |
| `GET /api/tickets/{id}/` — staff | 2 | 2 | 0 |
| `GET /api/tickets/{id}/` — requester | 2 | 2 | 0 |
| `GET /api/tickets/{id}/comments/` — staff | 4 | 4 | 0 |
| `GET /api/tickets/{id}/comments/` — requester | 4 | 4 | 0 |
| `GET /api/tickets/{id}/history/` — staff | 4 | 4 | 0 |
| `GET /api/tickets/{id}/history/` — requester | 4 | 4 | 0 |

**Resultado:** nenhuma das rotas e dos papéis medidos apresentou crescimento no número de consultas conforme o tamanho da página passou de 1 para 20 elementos. Os testes protegem essa propriedade e falham se o número de queries crescer mais de uma unidade.

## Experimento de N+1 — serializers isolados

Foi criado um experimento **contrafactual**, executando diretamente os serializers sobre querysets equivalentes **com e sem** `select_related`, com vinte objetos.

| Serializador | Queryset sem `select_related` | Queryset com `select_related` |
| --- | ---: | ---: |
| `TicketSerializer` | 21 | 1 |
| `TicketCommentSerializer` | 21 | 1 |

Aqui, 21 significa uma consulta para os vinte registros e vinte consultas adicionais para relacionamentos referenciados na serialização. `select_related` resolveu esses acessos por JOIN, em uma única consulta. A comparação é **do serializer**, não o custo completo do endpoint HTTP.

## Decisão de engenharia

O código anterior ao CHM-301 já utilizava corretamente:

- `TicketViewSet.get_queryset()`: `select_related("requester", "assignee")`;
- `TicketCommentListCreateView.get_queryset()`: `select_related("author")`;
- `TicketAuditHistoryView`: usa os snapshots `actor_username` e `actor_was_staff`, sem consultar o usuário para cada evento.

**Não houve alteração desnecessária de código de produção**: a otimização já existia, e sua eficácia foi comprovada com medidas. Não se recomenda `prefetch_related` nos endpoints atuais porque os serializers não navegam coleções reversas de relações nesses acessos.

## Validação

- GitHub Actions Python 3.10, 3.11 e 3.12: **70 testes verdes** por versão.
- Ruff, Django system check e migrations check: verdes.
- Cobertura de código da aplicação no CI: **95,2%**.

O relatório do CI é o baseline reproduzível. A validação Windows é feita separadamente antes do merge.

## Limitações e próximos passos

- A medição é de **quantidade de consultas**, não duração em milissegundos, consumo de memória ou carga simultânea.
- SQLite em CI não equivale ao PostgreSQL de produção; índices, planos de execução e latência de rede são diferentes.
- Os testes usam no máximo vinte objetos por página; não demonstram comportamento de milhares de páginas ou alta concorrência.
- Autenticação e paginação fazem parte do número de consultas do endpoint; portanto não se deve comparar os totais diretamente com o experimento dos serializers.
- Benchmarks de PostgreSQL, índices e transações pertencem ao **CHM-302** e à validação posterior em PostgreSQL real no **CHM-403**.
