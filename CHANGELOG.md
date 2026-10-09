# Changelog

Este changelog registra alterações verificáveis da Chamados API.
Adotamos [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
e versionamento semântico com sufixo de pré-release `-local.1`.

## [Unreleased] — correções sob revisão (PR #33)

### Fixed
- Evita novos avisos da outbox para responsáveis que deixaram de ser equipe ou foram desativados.
- Valida transições de status na edição pelo Django Admin; alterações efetivas de status, prioridade e atribuição registram auditoria e outbox.
- Impede troca de solicitante de um chamado já existente pelo formulário Django Admin, que contornaria a autorização da API.

### Tests
- Novas regressões de privilégios de destinatários e de edição/criação no Django Admin.

### Compatibility
- Permanece permitido à equipe escolher o status inicial na criação de chamados; não foram alteradas rotas, schemas JSON ou migrações.
- Atualizações diretas por `QuerySet.update()` e alterações administrativas de comentários não são auditadas automaticamente.

## [v1.0.0-local.1] — 2026-10-09

### Added
- Coleção Postman importável com placeholders sem credenciais.
- Arquitetura atual, case de portfólio, guia de apresentação e
  documentação de evidências.
- Captura real do Swagger como artefato automatizado de CI (para
  visualizar, acesse a execução vinculada à release).
- GitHub Release de demonstração local (sem deploy público).

### Included from previous development sprints
- Autenticação JWT, controle de acesso por papéis, CRUD de chamados,
  comentários e histórico auditável.
- Validações de domínio, integridade relacional, otimizações ORM e
  logging estruturado com request ID.
- PostgreSQL 16, Redis e Celery Worker/Beat verificados em CI Docker.
- Transactional outbox e caixa de entrada privada de notificações.
- Processador local com comando Django sem necessidade de Redis.

### Known limitations
- Modo local depende da máquina ligada; sem URL pública.
- Sem TLS hospedado, backup/rollback de produção ou observabilidade
  de plataforma. CHM-601 continua aberta por decisão de não
  provisionar serviços pagos.
- Sem frontend dedicado ou notificações externas (e-mail/push).

Compare a versão com os relatórios do
[CI](https://github.com/ZaraTakion/chamados-api/actions) e com a
documentação em `docs/RELEASE_NOTES.md`.
