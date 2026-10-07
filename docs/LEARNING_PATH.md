# Trilha de Estudos Vinculada às Sprints

A regra desta trilha é simples: **estudar o que a tarefa atual exige**, em vez de abrir vários cursos em paralelo.

## Antes de começar

Enquanto a Bird estiver ativa, este documento é apenas referência. Não existe obrigação de estudar Chamados API em paralelo.

Quando o projeto for iniciado, mantenha **uma tarefa Doing por vez**.

## Sprint 01 — Testes e qualidade

### Estudar

- estrutura de testes do Django;
- `APITestCase` e cliente de API do DRF;
- diferença entre teste unitário e de integração;
- coverage;
- Ruff;
- fixtures/setup de teste sem excesso de acoplamento.

### Saber explicar ao final

- o que sua suíte protege;
- o que cobertura mede e o que ela não mede;
- por que CI é diferente de “funciona no meu PC”.

> Não é obrigatório migrar para pytest. O runner atual do Django é válido; qualquer troca precisa trazer benefício real.

## Sprint 02 — HTTP, DRF e domínio

### Estudar

- 400 vs 401 vs 403 vs 404 vs 409;
- autenticação vs autorização;
- lifecycle de serializers/views/permissions;
- regras de negócio fora de controllers/views;
- modelagem de estados;
- audit trail.

### Saber explicar ao final

- quem pode fazer cada ação e por quê;
- como uma transição inválida é impedida;
- por que histórico não deve depender apenas de logs.

## Sprint 03 — SQL, PostgreSQL e ORM

### Estudar

- SELECT, JOIN, GROUP BY;
- índices;
- foreign keys e constraints;
- transações/atomicidade;
- N+1;
- `select_related` vs `prefetch_related`;
- noções de `EXPLAIN`.

### Saber explicar ao final

- por que um índice foi criado;
- quantas queries um endpoint crítico executa;
- onde uma transação é necessária.

## Sprint 04 — Operação

### Estudar

- logging estruturado;
- correlation/request IDs;
- liveness vs readiness;
- variáveis de ambiente;
- segurança de settings Django;
- GitHub Actions com services/PostgreSQL.

### Saber explicar ao final

- como investigar um erro em produção;
- como o serviço informa que está vivo e que está pronto;
- como CI reduz risco de diferenças entre SQLite e PostgreSQL.

## Sprint 05 — Redis e Celery

### Estudar

- fila de tarefas;
- worker;
- broker;
- retries;
- timeout;
- idempotência;
- tarefas assíncronas vs síncronas.

### Saber explicar ao final

- por que uma notificação não precisa bloquear a request;
- o que acontece se o worker cair;
- como evitar duplicação de efeitos.

## Sprint 06 — Deploy e entrega

### Estudar

- processo de deploy;
- migrations em produção;
- rollback;
- logs;
- backups;
- smoke tests;
- documentação operacional.

### Saber explicar ao final

- como colocar o projeto no ar;
- como detectar falha;
- como voltar atrás;
- quais são as limitações atuais do sistema.

## Rotina sugerida por tarefa

Para cada issue:

1. **15–25 min:** estudar o conceito mínimo.
2. **Implementar uma parte pequena.**
3. Rodar teste.
4. Ler o diff.
5. Commit.
6. Repetir.
7. Ao terminar, explicar em suas próprias palavras:
   - problema;
   - decisão;
   - alternativa;
   - trade-off;
   - como foi testado.

Se você não consegue explicar a decisão, ela ainda não está pronta para ser usada como evidência profissional.
