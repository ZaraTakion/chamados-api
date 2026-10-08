# Status do Projeto

## Agora — Sprint 03: Banco e performance

- Sprint 00, Sprint 01 e Sprint 02: **Done**.
- Sprint 03: **ativa**.
- [CHM-301 #8](https://github.com/ZaraTakion/chamados-api/issues/8): **Done**, PR #22 merged.
- [CHM-302 #9](https://github.com/ZaraTakion/chamados-api/issues/9): **Doing** — único item ativo.
- Branch de trabalho: `perf/chm-302-database-integrity`.
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

## CHM-302 — Foco atual

Revisar índices, constraints e transações com base nos acessos reais e nas invariantes do domínio. Documentar hipóteses e medir planos/consultas antes e depois de qualquer otimização. Validar integridade sob SQLite e PostgreSQL, **sem confundir um banco com o outro**.

### Regras de aceitação

1. Mapear os índices existentes (implícitos e explícitos), filtros e ordenações.
2. Selecionar índices apenas com justificativa documentada.
3. Garantir invariantes relevantes do domínio no banco, com testes.
4. Revisar operações que exigem atomicidade e testar rollback.
5. Fazer verificação real em PostgreSQL; não usar SQLite como prova substituta.
6. Validar CI, migrations e Windows antes de merge.

CHM-301 está encerrado; CHM-302 é o único Doing. A Sprint 04 ainda não começou.
