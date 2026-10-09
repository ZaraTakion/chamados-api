# CHM-502 — Notificações internas assíncronas

## O que é entregue

Quando um chamado é criado, atribuído, muda de status, é resolvido ou recebe
comentário público, o sistema registra intenções de notificação em uma
tabela de outbox. Um worker Celery cria itens na caixa de entrada privada
dos destinatários: GET /api/notifications/ (requer JWT).

**Não são enviados e-mails, SMS ou notificações push nesta entrega.**
O canal é a inbox interna da API. A resposta não revela títulos, descrições,
conteúdo de comentários, endereços de e-mail, tokens ou dados de outro usuário.

## Fluxo confiável e sem bloqueio de broker na requisição

1. O endpoint salva o chamado, alteração e/ou comentário e os eventos de
   outbox dentro de transaction.atomic. Uma falha antes do commit desfaz
   tanto a alteração quanto os eventos pendentes.
2. Celery Beat, em serviço separado do Docker Compose, publica a tarefa
   tickets.deliver_pending_notifications a cada 30 segundos.
3. O worker lê exclusivamente eventos confirmados no banco e cria um item
   de TicketNotification por NotificationOutbox, dentro de uma transação.
4. A relação OneToOne da notificação com seu evento impede duplicatas após
   retries e recebimento concorrente; processed_at registra processamento.
5. Uma exceção de banco interrompe a transação do evento; na próxima
   execução, o evento ainda pendente pode ser recuperado.

Em comparação com chamar task.delay_on_commit() no request, o outbox com
polling evita qualquer tentativa de conexão com Redis durante a resposta HTTP.
Isso tolera a indisponibilidade de Redis e evita a janela em que a transação
já foi confirmada, mas o broker recusou a publicação. Não há garantia de
exactly-once para serviços externos; a garantia aqui é idempotência da
escrita da inbox no banco. O processamento é eventual (tipicamente dezenas
de segundos), não em tempo real.

## Regras de destinatários

- Chamado criado: equipe ativa, exceto o autor do chamado.
- Atribuição efetiva: novo responsável, exceto o próprio autor da ação.
- Mudança efetiva de status: solicitante, exceto o autor da ação.
- Resolvido: evento específico ticket_resolved, sem duplicar status_changed.
- Comentário público: solicitante e responsável (se houver), exceto autor.
- Nota interna: não gera notificação para usuários.
- Atualização sem mudança efetiva de status/atribuição: sem novo evento.

## Segurança

O worker não copia dados pessoais do chamado; cada evento contém somente
kind, referência do ticket, destinatário e metadados de controle. A rota
de leitura é autenticada e filtra sempre por request.user. Não há endpoint
de listagem pública do outbox nem entrega de notas internas.

## Resiliência e operação

- Limite de 100 eventos por execução, retries automáticos de falhas de
  banco (até 3, com backoff exponencial e jitter).
- Soft timeout de 20s e hard timeout de 30s.
- Reinício do broker ou worker: eventos pendentes permanecem no banco e
  serão coletados na próxima execução quando Beat e worker retornarem.
- Para monitorar atrasos, conferir outbox pendente e timestamps no banco
  via administração autorizada; logs do worker não devem expor payloads.
- O serviço scheduler deve ser executado uma única vez por deployment;
  múltiplas réplicas de Beat provocam agendamento redundante (o worker é
  idempotente, mas há custo desnecessário).

## Como executar e validar

Use Docker Compose com PostgreSQL, Redis, API, worker e scheduler:

    docker compose up --build -d
    docker compose logs --tail=100 worker scheduler

Após aplicar migrations, crie/atualize chamados por API autenticada.
Os eventos pendentes são materializados pelo worker e podem ser consultados
em GET /api/notifications/. Em testes sem Redis, execute:

    python manage.py test tickets.tests.test_notifications

Os testes cobrem rollback, privacidade, seleção de destinatários, ausência
de notas internas, repetição, retries e modo eager. O CI Docker executa a
entrega real através do Redis e do worker; o teste Windows usa SQLite.

## Limitações

O outbox garante persistência local, não substitui monitoramento em
produção. Redis/Celery não entregam exactly-once externamente. Não há
e-mail, web push, marcação de leitura nem política de expurgo nesta etapa;
esses pontos podem ser adicionados em versões posteriores, conforme uso.

## Aceite da CHM-502 — 08/10/2026

- CI 5/5 jobs verdes; worker real Redis/Celery executou entrega de outbox em caixa de entrada privada. PostgreSQL 16: 113 testes aprovados; SQLite Python 3.10–3.12: 113 encontrados, 112 passaram e 1 skip específico PostgreSQL; coverage CI 94,8%.
- QA Windows: Ruff, Django check e migrations check aprovados; 113 testes (112 passaram, 1 skip), 0 falhas; cobertura local **95,2%**.
- Backup SQLite: `data/db-backup-chm502-1791505810.sqlite3`, `PRAGMA integrity_check=ok`. Migration `tickets.0004_notifications` aplicada com sucesso, `showmigrations tickets` confirma 0001–0004 `[X]`.
- [PR #28 merged](https://github.com/ZaraTakion/chamados-api/pull/28), commit `29b06109`.
- Próxima Sprint 06: deploy de produção e liberação final com documentação de operação.
