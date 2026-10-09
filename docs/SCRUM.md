# Scrum — Chamados API

## Product Goal

Evoluir a Chamados API de uma API funcional de portfólio para um **backend Python/Django com qualidade próxima de produção**, capaz de demonstrar em processos seletivos:

- regras de negócio explícitas;
- testes confiáveis;
- PostgreSQL;
- qualidade automatizada;
- observabilidade;
- processamento assíncrono quando houver justificativa;
- deploy reproduzível;
- documentação técnica e evidências reais.

## Estado atual

**Status:** SPRINT 05 CONCLUÍDA — Sprint 06 em planejamento.

A Sprint 01 foi concluída: [CHM-101 #3](https://github.com/ZaraTakion/chamados-api/issues/3) e [CHM-102 #4](https://github.com/ZaraTakion/chamados-api/issues/4) estão Done e suas PRs foram mergeadas.

[CHM-201 #5](https://github.com/ZaraTakion/chamados-api/issues/5) está **Done** após PR #19 merged.

[CHM-202 #6](https://github.com/ZaraTakion/chamados-api/issues/6) está **Done**, após validação local e merge da PR #20.

[CHM-203 #7](https://github.com/ZaraTakion/chamados-api/issues/7) está **Done**, após 62 testes locais aprovados e merge da PR #21.

A Sprint 02 está encerrada. [CHM-301 #8](https://github.com/ZaraTakion/chamados-api/issues/8) está **Done**, após 70 testes aprovados no Windows e merge da PR #22.

[CHM-302 #9](https://github.com/ZaraTakion/chamados-api/issues/9) está **Done**, após aceite Windows e merge da PR #23. [CHM-401 #10](https://github.com/ZaraTakion/chamados-api/issues/10) está **Done**, PR #24 integrada após CI e QA Windows. CHM-402 #11 está Done, após PR #25 merged e QA Windows aprovado. [CHM-403 #12](https://github.com/ZaraTakion/chamados-api/issues/12) está **Done**, após validação do CI e merge da PR #26. [CHM-501 #13](https://github.com/ZaraTakion/chamados-api/issues/13) está **Done**, após QA Windows e merge da PR #27. [CHM-502 #14](https://github.com/ZaraTakion/chamados-api/issues/14) está **Done**, após CI/QA Windows, backup/migration `0004` e merge da PR #28. Próximo item planejado: [CHM-601 #15](https://github.com/ZaraTakion/chamados-api/issues/15); nenhum Doing no momento.

## Princípios de trabalho

1. **Uma tarefa Doing por vez.**
2. Não adicionar tecnologia apenas para aumentar a lista do currículo.
3. Toda mudança de comportamento precisa de teste.
4. Toda decisão relevante precisa ser explicável em entrevista.
5. CI vermelho bloqueia avanço.
6. Segurança e dados sensíveis não são negociáveis.
7. O README deve representar o estado real do projeto.
8. Preferir pequenas entregas revisáveis a grandes reescritas.

## Quadro Scrum

Usaremos cinco estados:

| Estado | Significado |
| --- | --- |
| Backlog | Trabalho planejado para o futuro |
| Ready | Próximo item refinado e sem bloqueios |
| Doing | Única tarefa sendo implementada |
| Review | Código concluído, aguardando validação/CI/revisão |
| Done | Critérios de aceite e Definition of Done cumpridos |

**WIP limit:** no máximo **1 item em Doing**.

## Definition of Ready

Um item pode sair de Backlog para Ready quando:

- objetivo está claro;
- critérios de aceite estão definidos;
- dependências anteriores estão concluídas;
- não depende de informação que ainda não existe;
- pode ser realizado em uma unidade de trabalho razoavelmente pequena;
- sabemos como validar o resultado.

A Definition of Done completa está em [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md).

## Cadência

Após a Bird:

- **Sprint:** aproximadamente 2 semanas;
- **Sprint Planning:** escolher somente o que cabe na sprint;
- **Daily pessoal:** 5 minutos para responder:
  - o que concluí;
  - qual é a próxima ação;
  - existe bloqueio?;
- **Sprint Review:** demonstrar comportamento e evidências;
- **Retrospectiva:** registrar o que manter, mudar e parar de fazer.

O calendário começa somente quando CHM-000 for fechado.

## Roadmap de Sprints

### Sprint 00 — Preparação

**Objetivo:** deixar o caminho profissional pronto sem iniciar implementação.

- [x] auditar estado atual do repositório;
- [x] criar backlog;
- [x] definir Scrum;
- [x] definir roadmap;
- [x] definir trilha de estudo;
- [x] definir Definition of Done;
- [x] concluir Bird;
- [x] fechar [CHM-000 #2](https://github.com/ZaraTakion/chamados-api/issues/2).

### Sprint 01 — Qualidade e baseline

**Status:** DONE — concluída em 08/10/2026.

**Done:** [CHM-101 #3](https://github.com/ZaraTakion/chamados-api/issues/3) e [CHM-102 #4](https://github.com/ZaraTakion/chamados-api/issues/4).

**Sprint Goal:** conseguir medir a qualidade atual antes de aprofundar a arquitetura.

- [CHM-101 #3](https://github.com/ZaraTakion/chamados-api/issues/3) — baseline de qualidade, cobertura e Ruff.
- [CHM-102 #4](https://github.com/ZaraTakion/chamados-api/issues/4) — ampliar matriz de testes.

**Resultado esperado:** CI mede qualidade e os principais fluxos possuem cobertura de regressão.

### Sprint 02 — Domínio e consistência

**Status:** DONE — encerrada em 08/10/2026.

**Done:** [CHM-201 #5](https://github.com/ZaraTakion/chamados-api/issues/5)

**Done:** [CHM-202 #6](https://github.com/ZaraTakion/chamados-api/issues/6)

**Done:** [CHM-203 #7](https://github.com/ZaraTakion/chamados-api/issues/7)

**Sprint Goal:** transformar status/permissões em regras de negócio explícitas.

- [CHM-201 #5](https://github.com/ZaraTakion/chamados-api/issues/5) — transições de estado.
- [CHM-202 #6](https://github.com/ZaraTakion/chamados-api/issues/6) — histórico auditável.
- [CHM-203 #7](https://github.com/ZaraTakion/chamados-api/issues/7) — erros e validações consistentes.

**Resultado esperado:** ciclo de vida do chamado é previsível, testável e auditável.

### Sprint 03 — Banco e performance

**Status:** DONE — concluída em 08/10/2026.

**Done:** [CHM-301 #8](https://github.com/ZaraTakion/chamados-api/issues/8)

**Done:** [CHM-302 #9](https://github.com/ZaraTakion/chamados-api/issues/9)

**Sprint Goal:** demonstrar uso consciente do ORM e PostgreSQL.

- [CHM-301 #8](https://github.com/ZaraTakion/chamados-api/issues/8) — medir e otimizar queries.
- [CHM-302 #9](https://github.com/ZaraTakion/chamados-api/issues/9) — índices, constraints e transações.

**Resultado esperado:** decisões de banco sustentadas por medidas, testes e integridade.

### Sprint 04 — Produção e observabilidade

**Status:** DONE — concluída em 08/10/2026. CHM-401, CHM-402 e CHM-403 entregues.

**Sprint Goal:** tornar a API diagnosticável e mais próxima de um serviço operável.

- [CHM-401 #10](https://github.com/ZaraTakion/chamados-api/issues/10) — logging estruturado e request ID.
- [CHM-402 #11](https://github.com/ZaraTakion/chamados-api/issues/11) — liveness/readiness e segurança.
- [CHM-403 #12](https://github.com/ZaraTakion/chamados-api/issues/12) — CI com PostgreSQL real.

**Resultado esperado:** serviço observável, configuração de produção explícita e CI mais representativo.

### Sprint 05 — Processamento assíncrono

**Status:** DONE — CHM-501 e CHM-502 concluídas em 08/10/2026.

**Sprint Goal:** introduzir fila somente depois que o núcleo síncrono estiver sólido.

- [CHM-501 #13](https://github.com/ZaraTakion/chamados-api/issues/13) — Redis + Celery.
- [CHM-502 #14](https://github.com/ZaraTakion/chamados-api/issues/14) — notificações assíncronas.

**Resultado esperado:** processamento em background com retries controlados e sem corromper o domínio.

### Sprint 06 — Release profissional

**Sprint Goal:** transformar o projeto em evidência de carreira publicamente demonstrável.

- [CHM-601 #15](https://github.com/ZaraTakion/chamados-api/issues/15) — deploy de produção e runbook.
- [CHM-602 #16](https://github.com/ZaraTakion/chamados-api/issues/16) — evidências de portfólio e release.

**Resultado esperado:** API implantada, documentada, reproduzível e pronta para currículo/entrevista.

## Ordem de execução

A ordem não é negociável sem uma razão técnica:

`CHM-000 → CHM-101 → CHM-102 → CHM-201 → CHM-202 → CHM-203 → CHM-301 → CHM-302 → CHM-401 → CHM-402 → CHM-403 → CHM-501 → CHM-502 → CHM-601 → CHM-602`

Podemos reavaliar o conteúdo de uma sprint durante a Planning, mas evitaremos pular fundamentos para chegar mais rápido a tecnologias “bonitas” no currículo.

## Primeiro dia após a Bird

Quando a Bird terminar:

1. abrir a `main` atual;
2. rodar a suíte existente;
3. conferir CI;
4. fechar CHM-000;
5. mover **somente CHM-101** para Doing;
6. criar branch `chore/chm-101-quality-baseline`;
7. implementar em passos pequenos;
8. abrir PR;
9. CHM-101 e CHM-102 concluídos; Sprint 01 finalizada e CHM-201 é o único item em Doing.


## Review e Retrospectiva — Sprint 01

- Qualidade: Ruff, Coverage e GitHub Actions adicionados.
- Suíte de regressão: 7 para 25 testes.
- CI: Python 3.10, 3.11 e 3.12 verdes.
- Cobertura da aplicação: 92,7% CI / 93,7% Windows.
- Funcionou: tarefas de escopo limitado, PR e teste local antes do merge.
- Melhorar: modelar regras de negócio separadas de views/serializers.
- Evitar: porcentagens infladas pela inclusão de arquivos de teste.


## Review e Retrospectiva — Sprint 02

- CHM-201: matriz de transições centralizada, com regras válidas e inválidas cobertas.
- CHM-202: histórico persistente de status, prioridade e responsável; transação e controle de acesso.
- CHM-203: respostas de erro padronizadas de forma aditiva, mantendo compatibilidade com os campos existentes.
- Suíte evoluiu de **25 para 62 testes**, todos aprovados no Windows e em Python 3.10–3.12 no CI.
- CHM-203: cobertura de **94,8% no CI** e **95,4% no Windows**.
- Manter: revisão por PR, regressão automatizada antes do merge e confirmação Windows.
- Melhorar: desempenho do tempo total de testes e evidências quantitativas de consultas.
- Evitar: supor melhoria de desempenho sem medir o número de queries antes/depois.


## Review e Retrospectiva — Sprint 03

- CHM-301: contagens SQL constantes em listagens/detalhes/comentários/histórico; regressões de N+1 cobertas.
- CHM-302: constraints de domínio, row lock restrito ao próprio ticket, revisão de índices sem otimizações especulativas.
- GitHub Actions: Python 3.10–3.12 (SQLite) e PostgreSQL 16 aprovados; teste específico de bloqueio executado no PostgreSQL.
- Validação Windows em 08/10/2026: SQLite com migration `0003` aplicada após backup; Ruff, check e migrations verdes; 75 testes encontrados (74 passaram, 1 skip), cobertura da aplicação de 95,8%.
- Manter: evidências de QA local antes de merge, backup anterior a migrações e decisões de índices baseadas em medições.
- Melhorar: investigar duração da suíte (~260s no Windows) e aprofundar testes operacionais/concorrência na Sprint 04.
- Próximo: refinar e iniciar CHM-401, respeitando WIP máximo de um Doing.


### CHM-401 — Review e aceite

- Logs HTTP JSON de campos controlados, request ID por requisição e resposta HTTP, correlação de erros 5xx.
- CI verde em SQLite/Python 3.10–3.12 e PostgreSQL 16: 82 testes por ambiente (SQLite: 81 aprovados, 1 ignorado; PostgreSQL: 82 aprovados), 94,3% coverage.
- QA Windows 08/10/2026: Ruff, Django check, migrations verdes; 82 testes descobertos (81 aprovados, 1 skip), 286.338s, 94,8% coverage.
- [PR #24](https://github.com/ZaraTakion/chamados-api/pull/24) integrada e Issue #10 fechada.
- Próximo: CHM-402, com atenção a liveness/readiness, segurança de configuração e testes de integração.

## Review e Retrospectiva — Sprint 04

- CHM-401: logging JSON allowlist e request ID, CI e Windows com 82 testes (um skip no SQLite).
- CHM-402: liveness/readiness e fail-closed production config, CI com 96 testes, Windows 95 aprovados e 1 skip, coverage 94,5%.
- CHM-403: migrations explícitas e readiness smoke em PostgreSQL 16, CI 4/4 jobs verde; 96 testes em PostgreSQL e 95+1 skip no SQLite.
- Manter: regressões automatizadas, PostgreSQL real no CI e separação clara entre validação local e de integração.
- Melhorar: documentação de infraestrutura operacional e diminuir tempo de suíte no Windows sem remover cobertura.
- Evitar: mudar comportamento de rota legada sem teste de compatibilidade.
- Próxima Sprint: CHM-501, Redis/Celery, com uma tarefa Doing por vez e integração após QA.


### CHM-501 — Review e aceite

- API e worker Celery configurados com broker Redis; tarefa de métricas agregadas de tickets é idempotente e read-only.
- CI: cinco jobs verdes, incluindo execução de tarefa por worker real no Docker Compose; 101 testes por ambiente (SQLite 100 passaram, 1 skip PostgreSQL; PostgreSQL 101 aprovados), cobertura CI 94,3%.
- Windows (08/10/2026): Ruff, check e migration check verdes; 101 testes encontrados, 100 aprovados e 1 skip, duração 288.867s, cobertura 94,7%.
- PR #27 squash merged no commit `49b549bc`; Issue #13 concluída.
- Próximo item: CHM-502 — integração segura de notificações após commit de transações, retries e idempotência.


## Review e retrospectiva — Sprint 05

- CHM-501: integração Redis/Celery, tarefa read-only idempotente, CI 5/5 jobs e QA Windows (101 testes, 100 aprovados/1 skip, coverage 94,7%). PR #27 integrada.
- CHM-502: inbox privada, outbox transacional, periódica Celery Beat, segurança por destinatário, retries e idempotência. CI 5/5 jobs (113 testes PostgreSQL/112+1 SQLite), QA Windows 113 testes (112 passaram/1 skip), **95,2% coverage**.
- Migração local: backup consistente e íntegro antes de `tickets.0004_notifications`; migration aplicada e verificada.
- [PR #28 integrada](https://github.com/ZaraTakion/chamados-api/pull/28), commit `29b06109`; Issues #13 e #14 fechadas.
- Retrospectiva: preservar integridade transacional; manter testes de integração com Redis real; fazer backup antes de mudanças de schema; manter WIP máximo 1.
- Sprint 06: CHM-601 (deploy com runbook) e CHM-602 (evidências, tag e release). Nenhuma implantação de produção é reivindicada antes de smoke test real.
