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

**Status:** SPRINT 01 ATIVA

O gate [CHM-000 #2](https://github.com/ZaraTakion/chamados-api/issues/2) foi concluído em **07/10/2026** após a finalização da Bird e validação da `main`.

A **Sprint 01 — Qualidade e baseline** está ativa.

CHM-101 foi concluído e merged.

Item atual em **Doing**: [CHM-102 #4](https://github.com/ZaraTakion/chamados-api/issues/4).

Os itens da Sprint 02 permanecem em Backlog enquanto CHM-102 não estiver Done.

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

**Status:** ATIVA

**Done:** [CHM-101 #3](https://github.com/ZaraTakion/chamados-api/issues/3)

**Doing:** [CHM-102 #4](https://github.com/ZaraTakion/chamados-api/issues/4)

**Sprint Goal:** conseguir medir a qualidade atual antes de aprofundar a arquitetura.

- [CHM-101 #3](https://github.com/ZaraTakion/chamados-api/issues/3) — baseline de qualidade, cobertura e Ruff.
- [CHM-102 #4](https://github.com/ZaraTakion/chamados-api/issues/4) — ampliar matriz de testes.

**Resultado esperado:** CI mede qualidade e os principais fluxos possuem cobertura de regressão.

### Sprint 02 — Domínio e consistência

**Sprint Goal:** transformar status/permissões em regras de negócio explícitas.

- [CHM-201 #5](https://github.com/ZaraTakion/chamados-api/issues/5) — transições de estado.
- [CHM-202 #6](https://github.com/ZaraTakion/chamados-api/issues/6) — histórico auditável.
- [CHM-203 #7](https://github.com/ZaraTakion/chamados-api/issues/7) — erros e validações consistentes.

**Resultado esperado:** ciclo de vida do chamado é previsível, testável e auditável.

### Sprint 03 — Banco e performance

**Sprint Goal:** demonstrar uso consciente do ORM e PostgreSQL.

- [CHM-301 #8](https://github.com/ZaraTakion/chamados-api/issues/8) — medir e otimizar queries.
- [CHM-302 #9](https://github.com/ZaraTakion/chamados-api/issues/9) — índices, constraints e transações.

**Resultado esperado:** decisões de banco sustentadas por medidas, testes e integridade.

### Sprint 04 — Produção e observabilidade

**Sprint Goal:** tornar a API diagnosticável e mais próxima de um serviço operável.

- [CHM-401 #10](https://github.com/ZaraTakion/chamados-api/issues/10) — logging estruturado e request ID.
- [CHM-402 #11](https://github.com/ZaraTakion/chamados-api/issues/11) — liveness/readiness e segurança.
- [CHM-403 #12](https://github.com/ZaraTakion/chamados-api/issues/12) — CI com PostgreSQL real.

**Resultado esperado:** serviço observável, configuração de produção explícita e CI mais representativo.

### Sprint 05 — Processamento assíncrono

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
9. CHM-101 concluído; CHM-102 é agora o único item em Doing.
