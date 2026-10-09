# Case de portfólio — Chamados API

## Descrição pronta para apresentar

**Chamados API — Backend de suporte técnico (Django REST Framework)**

API REST com autenticação JWT, controle de acesso por papéis, ciclo de vida
de chamados, comentários, histórico auditável, observabilidade estruturada
e notificações internas com outbox transacional. Construí testes de
regressão e CI em SQLite e PostgreSQL 16, incluindo integração real de
Redis/Celery em Docker. Preparei um modo **Local Demo** sem Redis para
permitir demonstrações funcionais em um computador Windows com poucos
recursos e sem infraestrutura paga.

**O que demonstra:** engenharia de backend, integridade de dados,
segurança de API, testes, automação, documentação técnica e trade-offs.

**Link para repositório:** https://github.com/ZaraTakion/chamados-api

**Versão:** `v1.0.0-local.1` — demonstração local; **não existe URL
pública de produção**.

## Evidências que podem ser verificadas

1. [Suíte CI](https://github.com/ZaraTakion/chamados-api/actions):
   matriz Python, PostgreSQL 16 e Docker Compose real.
2. [Teste end-to-end autenticado](../tickets/tests/test_local_demo_e2e.py):
   registro, JWT, criação do chamado, processo offline e inbox isolada.
3. [Coleção Postman](../postman/Chamados-API-Local-Demo.postman_collection.json):
   rotas reproduzíveis sem tokens armazenados.
4. [Guia de execução local](./LOCAL_DEMO.md) e [arquitetura](./ARCHITECTURE.md).
5. [Notas da versão](./RELEASE_NOTES.md) e CHANGELOG do repositório.
6. Captura de tela **real** do Swagger gerada em CI (ver
   [EVIDENCE.md](./EVIDENCE.md) após os jobs passarem).

## Demonstração técnica em uma entrevista

**60 segundos:** explique o problema (acompanhar atendimentos),
apresente Swagger, níveis de permissão e mostre as notificações privadas.
Diga que o ambiente é local e o CI cobre PostgreSQL/Redis.

**3–5 minutos:** execute o servidor local + comando
`process_notifications --watch`; autentique solicitante via Swagger
ou Postman, crie um ticket com dados fictícios, confirme o evento no
processador e leia a inbox como equipe. Mostre testes e permissões.

**Perguntas técnicas relevantes:**

- **Por que a outbox?** Evita perda de intenção quando HTTP já gravou a
  transação mas o broker está indisponível; escrita única do domínio
  e intenção na mesma transação.
- **Por que SQLite local e PostgreSQL CI?** O primeiro reduz custo e
  complexidade da demonstração; o segundo valida constraints,
  isolamento e comportamento compatível com sistemas relacionais.
- **Como evita duplicatas?** Índices de unicidade e escrita idempotente
  da inbox durante o consumo dos eventos.
- **Como impede vazamento de informações?** Querysets por papel e
  destinatário, tratamento de notas internas, logs que evitam PII e
  testes de autorização.
- **Qual principal limitação?** Não há deploy HTTPS/SLA em nuvem; o
  `runserver` é apenas de desenvolvimento e não deve ficar público.

## Texto curto para currículo

**Chamados API (Python, Django REST Framework, PostgreSQL, Redis/Celery)**
— Modelei API de suporte técnico com autenticação JWT, permissões
granulares, auditoria de tickets e notificações idempotentes. Implementei
CI com múltiplas versões do Python, SQLite/PostgreSQL e testes de
integração Docker, documentando um modo de demonstração local gratuita
com endpoints OpenAPI e coleção Postman.

As métricas de testes/cobertura específicas desta versão aparecem nas
[notas de release](./RELEASE_NOTES.md). Nunca anuncie hospedagem pública
sem haver domínio HTTPS realmente validado.
