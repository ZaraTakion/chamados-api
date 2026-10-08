# Status do Projeto

## Agora

**Chamados API está oficialmente em execução — Sprint 01.**

- Gate CHM-000: **Done**
- CHM-101: **Done e merged**
- Sprint ativa: **Sprint 01 — Qualidade e baseline**
- Doing: [CHM-102 #4](https://github.com/ZaraTakion/chamados-api/issues/4)
- Branch de trabalho: `test/chm-102-api-test-matrix`
- Regra WIP: **1 tarefa Doing por vez**

## Baseline concluída no CHM-101

- Ruff integrado;
- Coverage integrado;
- CI em Python 3.10, 3.11 e 3.12;
- 7 testes atuais verdes;
- 10/10 baterias de estabilidade verdes;
- cobertura CI: **89,9%**;
- cobertura local Windows: **90,7%**;
- validação local em Windows 10 + Python 3.12 concluída.

## CHM-102 — Escopo ativo

Objetivo: ampliar a matriz de testes da API e aumentar confiança nos fluxos críticos.

Prioridades:
- autenticação e refresh/blacklist;
- requester × staff;
- CRUD de chamados;
- comentários públicos/internos;
- filtros, busca, ordering e paginação;
- schema/OpenAPI;
- casos negativos e validações.

Achado herdado do CHM-101:
- warnings do drf-spectacular em `accounts.views.me` e `tickets.views.health`.

O CHM-102 deve eliminar ou justificar esses warnings sem alterar comportamento funcional.

## Próximo movimento

Trabalhar exclusivamente no CHM-102 até Review/Done.

A Sprint 02 só começa quando CHM-102 estiver concluído.


## CHM-102 — Review

Validação automatizada concluída:

- suíte ampliada de **7 para 25 testes**;
- Python 3.10: verde;
- Python 3.11: verde;
- Python 3.12: verde;
- Ruff: verde;
- Django system check: verde;
- migrations check: verde;
- schema OpenAPI sem warnings do drf-spectacular;
- cobertura de código da aplicação: **92,7%**;
- 261 statements, 14 misses, 40 branches e 6 partial branches.

### Ajuste metodológico de cobertura

No CHM-101, o Coverage ainda incluía arquivos de teste no cálculo. O CHM-102 corrige isso e passa a excluir `tests.py` e `tests/`, então o percentual de 92,7% representa o código da aplicação. Por essa mudança metodológica, o percentual antigo não deve ser comparado diretamente como se usasse o mesmo denominador.

### Review pendente

- validação local no Windows: **concluída**.

### Validação local — Windows 10 / Python 3.12

- Ruff: verde;
- Django system check: verde;
- migrations check: verde;
- suíte: **25 testes verdes**;
- tempo local: 86.039s;
- cobertura local da aplicação: **93,7%**;
- 261 statements, 12 misses, 40 branches e 7 partial branches;
- nenhum warning `unable to guess serializer` do drf-spectacular.

O texto `unable to guess serializer` digitado após o relatório foi interpretado pelo CMD como comando e não representa warning da execução.

**CHM-102 está pronto para merge e encerramento da Sprint 01.**
