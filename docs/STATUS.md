# Status do Projeto

## Agora — Sprint 04: Produção e observabilidade (planejamento)

- Sprints 00, 01, 02 e 03: **Done**.
- [CHM-301 #8](https://github.com/ZaraTakion/chamados-api/issues/8): **Done**, PR #22 merged.
- [CHM-302 #9](https://github.com/ZaraTakion/chamados-api/issues/9): **Done**, PR #23 merged, validação Windows aprovada.
- Próximo item planejado: [CHM-401 #10](https://github.com/ZaraTakion/chamados-api/issues/10) (ainda não iniciado).
- WIP limit: uma tarefa Doing por vez.

## CHM-301 — Evidências concluídas

- Testes de regressão contra N+1 para listagem e detalhe de chamados, comentários e histórico.
- Contagens de consultas iguais com 1 e 20 registros: listagem 3, detalhe 2, comentários 4, histórico 4.
- Sem JOIN: 21 consultas para 20 objetos; com `select_related`: 1 consulta (tickets e comentários).
- Nenhuma alteração de código de produção foi necessária: `select_related` já estava implementado corretamente.
- CI Python 3.10, 3.11 e 3.12 verde, **70 testes**, **95,2% de cobertura**.
- Windows/Python 3.12: **70/70 testes** em 245.393s, Ruff/check/migrations verdes, **95,8% de cobertura local**.
- [Relatório de baseline e limites da medição](./ORM_QUERY_BASELINE.md).
- PR #22: squash merge concluído.

## CHM-302 — Entrega concluída

Foram revisados índices, adicionadas constraints e corrigido o bloqueio de linha para PostgreSQL, com testes de integridade nas duas engines. Nenhum ganho de latência foi alegado sem medição.

### Critérios de aceitação verificados

1. Mapear os índices existentes (implícitos e explícitos), filtros e ordenações.
2. Selecionar índices apenas com justificativa documentada.
3. Garantir invariantes relevantes do domínio no banco, com testes.
4. Revisar operações que exigem atomicidade e testar rollback.
5. Fazer verificação real em PostgreSQL; não usar SQLite como prova substituta.
6. Validar CI, migrations e Windows antes de merge.

CHM-301 e CHM-302 estão encerrados. Sprint 03 concluída em 08/10/2026; Sprint 04 aguarda início de CHM-401.

## CHM-302 — Resultados da validação

- Migration `0003_database_integrity`: restrições de domínio para status, prioridade e tipo de evento.
- `select_for_update(of=("self",))`: lock somente da linha do ticket, compatível com `assignee` anulável.
- CI: 75 testes verdes em Python 3.10–3.12 (SQLite), um teste específico PostgreSQL é pulado nesses ambientes.
- PostgreSQL 16 real no GitHub Actions: **75 testes aprovados**, incluindo cenário de lock com responsável nulo.
- Ruff, Django check, migrations check verdes.
- Coverage da aplicação: **95,2%**.
- Índices atuais revisados; nenhum composto novo adicionado sem comprovação de ganho.
- Documento de decisões: [DATABASE_INTEGRITY.md](./DATABASE_INTEGRITY.md).
- Windows/SQLite: backup local concluído antes da migration; `tickets.0003_database_integrity` aplicada com sucesso.
- Windows: Ruff/check/migrations verdes; suíte encontrou **75 testes**, **74 aprovados e 1 skip específico PostgreSQL**, em **259.988s**; **95,8% de cobertura** (391 statements, 13 misses, 88 branches, 7 partial branches).
- PR #23: [squash merge concluído](https://github.com/ZaraTakion/chamados-api/pull/23) (commit `10c08a9`). Issue #9 fechada.
