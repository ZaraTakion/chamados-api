# Evidências técnicas — v1.0.0-local.1

As evidências deste projeto são produzidas com dados **sintéticos**
em CI ou em localhost. Nenhum print gerado por IA substitui execução
real. Nenhuma URL de produção é alegada.

## Testes automatizados reais

- **GitHub Actions:** [histórico de CI](https://github.com/ZaraTakion/chamados-api/actions/workflows/tests.yml).
- **Fluxo autenticado:** `tickets/tests/test_local_demo_e2e.py`,
  verifica `POST /api/auth/register/`, JWT real,
  `POST /api/tickets/` com HTTP 201, outbox processada sem Redis,
  `GET /api/notifications/` autenticado, isolamento entre usuários
  e HTTP 401 para acesso anônimo.
- **PostgreSQL 16:** suíte executada em banco real no CI.
- **Redis+Celery:** serviço real com PostgreSQL em Docker Compose CI.
- **Swagger:** o job Docker CI captura `swagger-real-ci.png` por navegador
  Chrome headless, a partir de `http://127.0.0.1:8000/api/docs/`
  em serviço efetivamente em execução, e disponibiliza o arquivo
  como artefato `swagger-ci-capture`. O arquivo pode ser anexado à
  GitHub Release local depois de CI verde.

Os números definitivos da execução de release devem ser lidos no CI
que aponta para o commit/tag da versão, e não inferidos de um mockup.

## Testes locais observados (usuário — 09/10/2026)

- Swagger `/api/docs/` HTTP 200, OpenAPI `/api/schema/` HTTP 200.
- Registro HTTP 201, login JWT HTTP 200.
- `POST /api/tickets/` criou `CH-000001` (HTTP 201).
- SQLite confirmou: **Eventos: 1 | Processados: 1 | Notificacoes: 1**.
- Processador `--watch --interval 10` rodou ciclos sem Redis.
- Ruff, Django check e seis testes focados Windows: aprovados.

**Não observado:** GET da inbox diretamente pelo navegador Windows do
proprietário. O comportamento equivalente é testado por um cliente HTTP
real autenticado via JWT em banco temporário no GitHub Actions.

## Como conferir a captura

1. Abra a execução dos testes do commit da release em
   [GitHub Actions](https://github.com/ZaraTakion/chamados-api/actions).
2. Em **Artifacts**, abra `swagger-ci-capture` para ver a captura PNG
   produzida pelo navegador no CI, sem dados de usuários reais.
3. Depois de publicada a release, o asset
   `swagger-real-ci.png` também ficará disponível na sua página.

A captura comprova a interface Swagger no ambiente de testes, **não**
seu funcionamento na internet. O projeto requer `runserver` local
para uso no Windows e continua sem hospedagem pública.
