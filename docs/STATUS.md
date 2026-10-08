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

## Implementação do CHM-101

A branch agora prepara:

- dependências de desenvolvimento separadas em `requirements-dev.txt`;
- Ruff configurado em `pyproject.toml`;
- Coverage configurado para medir código da aplicação e branches;
- GitHub Actions executando lint + checks + testes + cobertura em Python 3.10–3.12;
- artifact `coverage.json` por versão do Python;
- comandos locais documentados no README.

A baseline numérica de cobertura será registrada após a primeira execução verde desta configuração.

## Próximo movimento

Validar o CHM-101 no CI e no Windows local. Se ambos passarem, registrar a baseline, colocar o issue em Review e preparar o merge.

CHM-102 só poderá entrar em Doing depois disso.
