# CHM-601 — Preparação de deploy no Railway

**Status:** preparação técnica; nenhum ambiente de produção é considerado
publicado até que haja URL HTTPS e smoke tests reais registrados no issue #15.

## Arquitetura e custos

A implantação proposta usa **cinco serviços** no mesmo projeto/environment:

1. `Postgres` — banco persistente privado, com backups configurados.
2. `Redis` — broker/result backend privado, sem acesso TCP público.
3. `chamados-api-web` — único serviço com domínio público.
4. `chamados-api-worker` — consumidor Celery, privado.
5. `chamados-api-beat` — instância **única** do scheduler, privada.

O Railway é um serviço externo que pode gerar custos contínuos, inclusive
com mais de um serviço em execução. **Não iniciar um deploy nem habilitar
recursos faturáveis sem aprovação do proprietário da conta.** Verificar
planos, limites, consumo e política de backups no painel antes de aprovar.

Documentação oficial: https://docs.railway.com/guides/django e
https://docs.railway.com/guides/docker-compose .

## Pré-requisitos

- PR de deploy aprovado, branch `main` verde no CI.
- Conta Railway autorizada e repositório GitHub conectado com permissões mínimas.
- Confirmação de custos, região, domínios e se o ambiente é demonstração
  pública ou prévia privada. Nunca publicar dados pessoais de produção.
- PostgreSQL e Redis criados **no mesmo projeto e environment** com rede
  privada; não habilitar TCP proxy público para bancos.
- Disponibilidade de backups persistentes do Postgres, restauração testada
  e responsáveis por incidentes definidos antes de dados reais.

## Configuração dos serviços a partir de uma única base de código

Criar três serviços GitHub apontando para `ZaraTakion/chamados-api` na
branch `main`, todos com o `Dockerfile` da raiz. Em cada serviço,
configurar o campo **Config as Code** para a rota correspondente (começa
com `/`) no mesmo repositório:

| Serviço | Config as Code | Entrada |
| --- | --- | --- |
| Web | `/deploy/railway-web.json` | Dockerfile CMD (Gunicorn + `$PORT`) |
| Worker | `/deploy/railway-worker.json` | Celery worker, concorrência 1 |
| Scheduler | `/deploy/railway-beat.json` | Celery Beat (uma réplica) |

O web executa `python manage.py migrate --noinput` no **pre-deploy**
e só recebe tráfego depois de `GET /api/health/ready/` responder HTTP 200.
Worker e Beat **não executam migrations**, evitando concorrência de
alteração de schema. Não escalar Beat horizontalmente.

**Variáveis privadas**: cadastrar no painel do Railway, em cada um dos
três serviços Django, sem copiar `.env.example` nem publicar valores:

| Nome | Valor esperado |
| --- | --- |
| `DJANGO_DEBUG` | `false` |
| `DJANGO_SECRET_KEY` | segredo único, aleatório e privado, com 50+ caracteres |
| `DJANGO_ALLOWED_HOSTS` | domínio exato da Web e `healthcheck.railway.app`, separados por vírgula |
| `DJANGO_SECURE_SSL_REDIRECT` | `true` |
| `DATABASE_URL` | referência `${{Postgres.DATABASE_URL}}` |
| `CELERY_BROKER_URL` | referência `${{Redis.REDIS_URL}}` |
| `CELERY_RESULT_BACKEND` | referência `${{Redis.REDIS_URL}}` |
| `APP_LOG_LEVEL` | `INFO` |
| `DJANGO_TRUST_PROXY_SSL_HEADER` | `true` **apenas após confirmar** que o proxy sanitiza `X-Forwarded-Proto` |
| `DJANGO_HSTS_SECONDS` | começar em `0`, alterar apenas após teste de TLS e domínio |

As expressões `${{Service.VARIABLE}}` acima são **referências de
variáveis do Railway**, não URLs literais. O nome `Postgres`/`Redis`
deve corresponder exatamente ao serviço criado no projeto.

A URL de resultados Celery pode compartilhar Redis com o broker; Celery
usa chaves distintas. Backups e alta disponibilidade requerem configuração
própria. O Railway atual fornece serviço Postgres com suporte a SSL; manter
a validação TLS da conexão do Django para produção.

`DJANGO_ALLOWED_HOSTS` deve listar o hostname exato da Web (por exemplo,
o domínio gerado no ambiente); o hostname `healthcheck.railway.app`
precisa estar autorizado para o probe do Railway. Nunca usar `*`.

## HTTPS e healthcheck

- Apenas o web recebe domínio e tráfego público; não publicar outros serviços.
- O Gunicorn já usa a variável `PORT` injetada pelo Railway.
- A plataforma verifica `GET /api/health/ready/` e exige 200.
- A aplicação redireciona requisições HTTP normais para HTTPS. Somente
  `/api/health/live/` e `/api/health/ready/` são isentas do
  **redirecionamento** para permitir probes internos HTTP; não expõem PII.
- Confirmar cabeçalho de protocolo enviado pelo proxy ANTES de habilitar
  `DJANGO_TRUST_PROXY_SSL_HEADER`. O proxy precisa remover qualquer
  `X-Forwarded-Proto` controlado pelo cliente e inserir um valor confiável.
- Ativar HSTS em etapas apenas com HTTPS já validado. HSTS com um domínio
  errado pode bloquear usuários durante bastante tempo.

Referências: https://docs.railway.com/deployments/healthchecks e
https://docs.railway.com/config-as-code .

## Ordem de implantação

1. Revisar fatura e configurar Postgres (persistência, backup) e Redis
   (privado, retenção apropriada).
2. Criar e configurar Web, Worker e Beat a partir da `main`, **sem
   habilitar autodeploy de produção antes do aceite**.
3. Configurar segredos e referências para os três. Usar o mesmo
   `DJANGO_SECRET_KEY` seguro em todos. Manter Beat com uma réplica.
4. Implantar **Web primeiro**; o pre-deploy aplica migrations.
5. Confirmar que a readiness devolve 200 e que o domínio oferece HTTPS.
6. Implantar Worker e Beat somente após o schema ter sido aplicado.
7. Executar smoke checks públicos, em uma máquina com rede:
   `python scripts/smoke_deploy.py https://DOMINIO_REAL`.
8. Em conta de demonstração e com dados não sensíveis, autenticar e
   criar um chamado, atualizar status, verificar notificação eventual;
   conferir logs seguros (sem senhas, tokens, bodies).
9. Registrar URL, commit deployado, status CI, resultados dos probes,
   comportamento do Worker/Beat e backups no issue CHM-601.
10. Somente depois habilitar publicação/autodeploy conforme preferência
    e concluir Definition of Done.

O script de smoke usa somente GET públicos, valida readiness, liveness,
Request ID, no-store, schema e Swagger. **Não substitui** prova de
autenticação, entrega pelo worker, backups e monitoramento.

## Bloqueios externos

A criação de serviços, conexão GitHub com Railway, autorização de
faturamento, provisionamento real, segredos e URLs precisam ser efetuados
na conta do proprietário. Se a integração do Railway estiver conectada ao
ChatGPT e autorizada, esses passos podem ser executados na conta. Sem isso,
a preparação e testes de CI são verificáveis, mas **não o deploy real**.
