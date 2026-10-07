# Roadmap Profissional — Chamados API

## Visão

Este roadmap usa o Chamados API como projeto principal para desenvolver e demonstrar competências de **Backend Python Júnior → Backend Developer**.

A API já possui uma base funcional:

- Django 5.2 e Django REST Framework;
- JWT com refresh/blacklist;
- isolamento de chamados por solicitante;
- fluxo de equipe via `is_staff`;
- filtros, busca, ordering e paginação;
- comentários públicos e internos;
- OpenAPI/Swagger;
- SQLite local e PostgreSQL via Docker Compose;
- Dockerfile com usuário não-root;
- GitHub Actions em Python 3.10, 3.11 e 3.12.

Portanto, a próxima fase não é “adicionar CRUD”. É aprofundar **engenharia de software, confiabilidade e operação**.

## Horizonte

Se cada sprint durar aproximadamente duas semanas, o percurso completo ocupa cerca de **12 semanas / 90 dias** após a conclusão da Bird.

| Período | Foco | Evidência de carreira |
| --- | --- | --- |
| Semanas 1–2 | Qualidade e baseline | cobertura, lint, testes |
| Semanas 3–4 | Domínio | regras, auditoria, erros |
| Semanas 5–6 | Banco e performance | SQL/ORM, índices, transações |
| Semanas 7–8 | Produção | logs, health, PostgreSQL CI |
| Semanas 9–10 | Assíncrono | Redis, Celery, notificações |
| Semanas 11–12 | Release | deploy, runbook, demo |

## O que este projeto deverá provar no final

### Python / Django

- organização de projeto;
- views/serializers/permissions;
- validações;
- tratamento de exceções;
- settings por ambiente;
- testes automatizados.

### HTTP / REST

- autenticação vs autorização;
- códigos HTTP coerentes;
- paginação, filtros e busca;
- contrato de erros;
- OpenAPI.

### PostgreSQL / SQL

- índices justificados;
- constraints;
- transações;
- queries observadas e otimizadas;
- CI contra banco real.

### Engenharia

- CI;
- lint;
- cobertura;
- Docker;
- configuração segura;
- logs;
- health/readiness;
- documentação.

### Sistemas assíncronos

- Redis;
- Celery;
- idempotência;
- retries/timeouts;
- tarefas que não bloqueiam requisições HTTP.

### Produção

- deploy;
- migrations;
- HTTPS;
- segredos por ambiente;
- runbook;
- smoke tests;
- limitações conhecidas.

## Fora de escopo até o release

Para preservar foco, estes assuntos **não entram** antes de existir necessidade real:

- Kubernetes;
- Kafka;
- microserviços;
- GraphQL;
- Terraform;
- event sourcing;
- arquitetura distribuída complexa.

Eles podem virar roadmap futuro, mas não são requisitos para transformar este projeto em uma excelente evidência de Backend Python Júnior.

## Métricas de progresso

Não usaremos quantidade de commits como indicador principal.

Acompanharemos:

- testes verdes;
- cobertura e regressões relevantes;
- quantidade de fluxos críticos testados;
- queries por endpoint crítico;
- ausência de N+1;
- CI em SQLite/PostgreSQL;
- tempo de recuperação de falhas documentado;
- capacidade de outra pessoa executar o projeto pelo README;
- capacidade de explicar as decisões em uma entrevista.

## Critério de conclusão do roadmap

O roadmap termina quando:

1. Sprint 06 estiver Done;
2. houver deploy demonstrável;
3. README representar integralmente a arquitetura atual;
4. Swagger/API puderem ser apresentados em entrevista;
5. currículo e portfólio puderem apontar para evidências reais;
6. limitações forem documentadas honestamente;
7. o projeto tiver uma release/tag estável.
