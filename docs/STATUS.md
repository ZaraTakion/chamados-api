# Status do Projeto

## Agora

**Chamados API está oficialmente em execução — Sprint 01.**

- Gate CHM-000: **Done** em 07/10/2026
- Sprint ativa: **Sprint 01 — Qualidade e baseline**
- Doing: [CHM-101 #3](https://github.com/ZaraTakion/chamados-api/issues/3)
- Próximo item em Backlog: [CHM-102 #4](https://github.com/ZaraTakion/chamados-api/issues/4)
- Branch de trabalho: `chore/chm-101-quality-baseline`
- Regra WIP: **1 tarefa Doing por vez**

## Sprint Goal

Conseguir medir a qualidade atual da API antes de aprofundar arquitetura ou regras de negócio.

## CHM-101 — Escopo ativo

- adicionar medição de cobertura;
- adicionar lint com Ruff;
- documentar comandos locais;
- integrar verificações ao CI sem remover a matriz Python existente;
- registrar baseline inicial;
- não alterar comportamento funcional da API.

## Base validada antes da Sprint 01

A `main` está estável e o último CI antes da abertura da sprint terminou com **success** em Python 3.10, 3.11 e 3.12.

O projeto já possui:

- Django REST Framework;
- JWT;
- permissões requester/staff;
- filtros/busca/ordering/paginação;
- comentários internos;
- OpenAPI/Swagger;
- Docker;
- PostgreSQL via Compose;
- health endpoint;
- testes automatizados;
- GitHub Actions em Python 3.10–3.12.

## Próximo movimento

Trabalhar exclusivamente no CHM-101 até ele chegar a Review/Done.

CHM-102 só poderá entrar em Doing depois disso.
