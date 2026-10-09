# Demonstração local gratuita — Chamados API

Esta é uma **demonstração funcional na própria máquina**. Não exige
Railway, Render, domínio, Docker, servidor Redis ou pagamentos. O código
Django/DRF, as migrações e a estrutura do banco permanecem os mesmos.
SQLite armazena os chamados e a outbox persistentemente em
`data/db.sqlite3`.

**Importante:** não é deploy público de produção. O servidor `runserver`
é apenas para desenvolvimento e deve usar `127.0.0.1`. O projeto mantém
a arquitetura Redis/Celery para ambientes Linux que puderem hospedá-la;
a alternativa local não remove essas dependências do repositório.

## Pré-requisitos

- Python e `.venv` existentes, com dependências de `requirements-dev.txt`.
- Windows CMD (não requer terminal como administrador).
- Branch com o modo local já integrada ou selecionada.
- Em desenvolvimento, `DJANGO_DEBUG=true` (valor padrão local).
- Se houver `DATABASE_URL` no ambiente, ele deve apontar para um banco
  autorizado; para usar o SQLite local, **não** defina `DATABASE_URL`.
- Se o banco ainda não existir, executar `python manage.py migrate`.

## Terminal 1 — API HTTP local

Na pasta do projeto, com `.venv` ativada:

```bat
python manage.py check
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

No navegador:

- Documentação interativa: http://127.0.0.1:8000/api/docs/
- Schema OpenAPI: http://127.0.0.1:8000/api/schema/
- Saúde (liveness): http://127.0.0.1:8000/api/health/live/
- Banco disponível: http://127.0.0.1:8000/api/health/ready/

**Não** usar `0.0.0.0`, abrir portas no roteador ou expor `runserver`
pela internet. A API exige JWT para os endpoints privados. Use contas
e chamados de demonstração, nunca dados pessoais de terceiros.

## Terminal 2 — Notificações sem Redis

Abrir outra janela CMD, na mesma pasta, com `.venv` ativada:

```bat
python manage.py process_notifications --watch --interval 30
```

O comando é um **processo separado do HTTP**, portanto a API segue
respondendo enquanto ele consulta a outbox e cria notificações privadas.
O tempo usual entre a gravação de um evento e sua aparição na inbox é
de até cerca de 30 segundos enquanto o processo estiver em execução.

Para processar uma vez e encerrar:

```bat
python manage.py process_notifications
```

Para parar o modo contínuo, pressionar `Ctrl+C`. Ao reiniciar, eventos
ainda pendentes continuam no SQLite e poderão ser processados. Cada
evento só origina uma notificação por destinatário. O comando permite
intervalo entre 1 e 3600 segundos e imprime apenas contagens, sem
títulos, mensagens, senhas ou outros conteúdos.

Se o banco estiver temporariamente indisponível, o modo contínuo
registra mensagem genérica e tenta de novo no próximo ciclo, sem perder
o evento. Para **produção**, a proteção `DJANGO_DEBUG=false` bloqueia
este comando: usar o worker/Beat Celery ou alternativa operacional
planejada e auditada.

**Não executar** este processador local contra um banco que já esteja
sendo processado por Celery Beat/Worker. No Windows SQLite, usar somente
uma instância do comando com `--watch` de cada vez.

## Fluxo funcional que você pode demonstrar

1. Acesse a Swagger UI, crie uma conta solicitante e autentique via JWT.
   Se precisar testar notificações destinadas à equipe, tenha uma conta
   `is_staff=True` criada através do comando `createsuperuser` ou
   de um administrador existente.
2. Faça `POST /api/tickets/` com título e descrição de teste.
3. O evento criado é persistido na outbox na mesma transação do chamado.
4. O Terminal 2 cria a notificação para a equipe, sem chamar Redis.
5. Autentique como destinatário e consulte `GET /api/notifications/`.
6. Faça atualização de status, atribuição ou comentário público para
   testar os demais tipos; notas internas não geram aviso ao solicitante.

Caso o Terminal 2 esteja desligado, as notificações aparecem quando
ele voltar a processar a outbox. O browser Swagger não cria um frontend
customizado: ele é uma interface para demonstrar e testar a API.

## Smoke e testes

Em um terceiro CMD, enquanto a API estiver no ar:

```bat
python scripts/smoke_deploy.py http://127.0.0.1:8000 --allow-http-local
```

Testes automatizados focados no modo local:

```bat
ruff check .
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test tickets.tests.test_offline_demo
```

As verificações com Docker/Linux seguem no CI, enquanto os comandos
acima cobrem o cenário de baixo consumo de RAM no Windows.

## Limitações e escopo real

- Zero mensalidade e nenhum recurso de nuvem criado, mas depende do
  computador permanecer ligado e dos processos estarem abertos.
- Sem URL pública e sem disponibilidade 24/7. `runserver` não serve
  para exposição pública nem para dados reais sensíveis.
- A inbox interna funciona com persistência e recupera eventos após
  interrupção, mas não envia emails, SMS ou push externo.
- SQLite e um único processador atendem à demonstração, não garantem
  escala, alta disponibilidade nem resiliência de produção.
- [CHM-601 #15](https://github.com/ZaraTakion/chamados-api/issues/15)
  permanece aberta para os critérios originais de produção (HTTPS,
  banco gerenciado, backups, monitoramento e URL real). A decisão de
  não gastar dinheiro é respeitada; esse passo pode ficar congelado.

## Evidências de aceite — versão local (09/10/2026)

- [PR #30](https://github.com/ZaraTakion/chamados-api/pull/30) integrada à `main`, commit `6585d2a`.
- [GitHub Actions 37873992540](https://github.com/ZaraTakion/chamados-api/actions/runs/37873992540): 6/6 jobs; 128 testes por ambiente (SQLite 127 passaram/1 skip, PostgreSQL 128 passaram), cobertura 94,2%.
- Teste Django de ponta a ponta: `python manage.py test tickets.tests.test_local_demo_e2e`. O teste cria dados descartáveis, autentica via JWT real e valida que só a equipe destinatária obtém a notificação em `GET /api/notifications/`; repetições não geram duplicatas.
- Evidência manual Windows: testes locais do processador 6/6 OK, Swagger 200, cadastro 201, JWT 200, chamado `CH-000001` criado com HTTP 201; consulta SQLite registrou `Eventos: 1 | Processados: 1 | Notificacoes: 1`.
- Não houve leitura HTTP da inbox diretamente no navegador do proprietário; esse comportamento foi testado automaticamente com contas sintéticas em banco temporário.
- Nenhum projeto, banco, worker, domínio ou recurso faturável foi provisionado no Railway. Esta entrega permanece **demonstração local**, não produção.

## Portfólio e pré-release local

A versão `v1.0.0-local.1` inclui coleção Postman sanitizada, visão de
arquitetura, case de recrutamento, changelog e evidência de CI com
captura real da interface Swagger. Consulte [PORTFOLIO.md](./PORTFOLIO.md),
[POSTMAN.md](./POSTMAN.md) e [EVIDENCE.md](./EVIDENCE.md).
A pré-release não indica disponibilidade pública: todos os usos reais
continuam em `127.0.0.1`.
