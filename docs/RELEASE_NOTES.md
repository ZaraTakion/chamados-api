# Chamados API v1.0.0-local.1 — Release local para portfólio

**Tipo:** pré-release de demonstração local, sem serviço público.
**Data:** 09/10/2026.
**Código:** branch `main`, tag `v1.0.0-local.1`.

## Destaques

- Django REST Framework com registro, autenticação JWT e revogação de
  refresh tokens.
- CRUD de chamados, permissões de equipe/solicitante, transições de
  status, prioridades, comentários e notas internas.
- Histórico auditável, erros padronizados, observabilidade com request ID,
  rotas health e OpenAPI/Swagger.
- Outbox transacional e notificações privadas idempotentes.
- **Modo Windows sem Redis:** `process_notifications --watch`,
  em processo independente da API.
- Docker Compose para PostgreSQL 16, Redis e Celery Worker/Beat validado
  em GitHub Actions; infraestrutura de Railway apenas preparada.
- Coleção Postman com valores placeholders, arquitetura e guia de demo.

## Qualidade e verificações

O aceite pré-release exige seis jobs verdes em GitHub Actions:
três versões do Python (3.10–3.12) com SQLite, PostgreSQL 16,
Redis/Celery com API HTTP real no Docker, e tipagem Railway IaC.
Também inclui teste JWT end-to-end do fluxo outbox → inbox sem Redis
e screenshot real do Swagger produzida em CI.

A execução anterior à CHM-602 encontrou **128 testes por ambiente**
(SQLite 127 passaram/1 skip, PostgreSQL 128 passaram), com **94,2%**
de cobertura no CI. Os números podem aumentar com os testes de
release adicionados nesta etapa; use os relatórios do commit/tag final
como referência definitiva.

## Uso

No Windows, com `.venv` e `requirements-dev.txt` instalados:

```bat
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

Em outro CMD, no mesmo ambiente:

```bat
python manage.py process_notifications --watch --interval 10
```

Swagger: http://127.0.0.1:8000/api/docs/

Documentação completa: [LOCAL_DEMO](./LOCAL_DEMO.md),
[POSTMAN](./POSTMAN.md), [ARCHITECTURE](./ARCHITECTURE.md) e
[PORTFOLIO](./PORTFOLIO.md).

## Limitações declaradas

- Não há deploy público HTTPS, banco gerenciado, monitoramento 24x7,
  backups/rollback de produção nem SLA.
- Não executar `runserver` publicamente. Processador local bloqueado
  com `DEBUG=False`; Redis/Celery permanecem recomendados para
  ambiente apropriado.
- Não há frontend próprio nem notificações por e-mail/push.
- O proprietário optou por **não contratar** hospedagem. A
  [CHM-601](https://github.com/ZaraTakion/chamados-api/issues/15)
  permanece aberta e bloqueada para produção, sem impedir esta release
  de portfólio local.

Nenhum token ou senha real deve integrar código, screenshots,
exemplos ou notas de release.

## Resultado de publicação verificado

- [Pré-release v1.0.0-local.1](https://github.com/ZaraTakion/chamados-api/releases/tag/v1.0.0-local.1) publicada com tag apontando ao commit `5edb6d8`.
- [CI do commit de lançamento](https://github.com/ZaraTakion/chamados-api/actions/runs/37879361318): seis jobs de qualidade/integração e o job de release aprovados; 133 testes no PostgreSQL; 132 pass + 1 skip SQLite; cobertura 94,2%.
- [Asset PNG real do Swagger](https://github.com/ZaraTakion/chamados-api/releases/download/v1.0.0-local.1/swagger-real-ci.png) anexado (74.540 bytes), gerado em navegador Chrome no runner CI sobre a API em execução.
- Nenhum serviço de produção criado; CHM-601 permanece aberta.
