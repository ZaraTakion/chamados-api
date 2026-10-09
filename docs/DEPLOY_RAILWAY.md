# CHM-601 — Deploy Railway (Infrastructure as Code)

**Estado:** configuração revisada; nenhum serviço novo de produção foi criado.
A publicação com domínio HTTPS, persistência, backups e smoke autenticado
será validada após aprovação explícita dos custos e do ambiente.

## Arquitetura

A aplicação usa cinco recursos privados no mesmo projeto e ambiente:

| Recurso | Processo | Acesso |
| --- | --- | --- |
| `Postgres` | Banco gerenciado e persistente | Somente rede privada |
| `Redis` | Broker e backend de resultados Celery | Somente rede privada |
| `chamados-api-web` | Django / Gunicorn | Único serviço público |
| `chamados-api-worker` | Celery Worker, concorrência 1 | Somente rede privada |
| `chamados-api-beat` | Celery Beat, 1 réplica | Somente rede privada |

**Importante:** esses cinco recursos podem gerar custos recorrentes. Não
aplicar o plano sem aprovar custos, backups, região e política de publicação.
Não reutilizar os serviços de outros projetos do workspace.

## Configuração reproduzível e atualizada

O Railway descontinuou o Config as Code (`railway.json` e
`railway.toml`) para serviços novos e recomenda **Infrastructure as Code**
com o arquivo [`.railway/railway.ts`](../.railway/railway.ts).
O pacote `railway` está declarado no `package.json` apenas para as
ferramentas de infraestrutura; **o backend continua sendo Python/Django**.

Para uma conta já autorizada, usar o CLI no projeto correto:

```bash
npm install
railway login
railway link
railway config plan
```

`railway config plan` consulta o Railway e mostra a alteração proposta sem
provisioná-la. **Não executar `railway config apply` antes de revisão e
autorização**, porque ele pode criar serviços pagos e bancos persistentes.

Também é possível configurar esses recursos com a integração Railway do
ChatGPT, mas apenas depois de confirmar projeto, ambiente e autorização de
custos. O arquivo IaC é a especificação desejada, não uma prova de que a
infraestrutura existe.

Fontes oficiais:
- https://docs.railway.com/infrastructure-as-code
- https://docs.railway.com/infrastructure-as-code/reference

## GitHub e segredos

A conta Railway precisa ter acesso de GitHub a
`ZaraTakion/chamados-api`, e `main` deve estar verde no CI.
Configurar na seção **Shared Variables** do novo ambiente, antes de
aplicar o plano:

- `DJANGO_SECRET_KEY`: segredo aleatório exclusivo, 50+ caracteres,
  sem enviá-lo para conversas, Git, prints ou logs.
- `DJANGO_ALLOWED_HOSTS`: domínio exato do web e
  `healthcheck.railway.app`, separados por vírgula, sem `*`.

O IaC referencia esses valores como `ctx.shared.DJANGO_SECRET_KEY`
e `ctx.shared.DJANGO_ALLOWED_HOSTS`; não os armazena no repositório.
Gerar o domínio público do Web antes de realizar o aceite final.
Após configurar o domínio, atualizar a variável shared de hosts.

A configuração aplica aos três processos:

- `DJANGO_DEBUG=false`;
- `DATABASE_URL` referenciando Postgres gerenciado;
- `CELERY_BROKER_URL` e `CELERY_RESULT_BACKEND` referenciando
  Redis gerenciado;
- `DJANGO_SECURE_SSL_REDIRECT=true`, `APP_LOG_LEVEL=INFO`;
- `DJANGO_HSTS_SECONDS=0` inicialmente.

**Não usar** os valores de `.env.example` em produção. Só ativar
`DJANGO_TRUST_PROXY_SSL_HEADER=true` após verificar que o proxy TLS
sobrescreve `X-Forwarded-Proto` e não aceita valor falso do cliente.
Sem essa confiança, o proxy pode causar redirecionamentos em loop ou
classificação insegura das requisições.

## Migrações e healthchecks

O Web executa `python manage.py migrate --noinput` no **pre-deploy**.
Um comando de pre-deploy que falhe bloqueia a promoção daquele deploy.
Worker e Beat não executam migrations. Os serviços usam o Dockerfile da
raiz do projeto; o Web usa o CMD de Gunicorn e a variável `PORT`.

O probe HTTP interno `GET /api/health/ready/` deve retornar 200.
Inclua `healthcheck.railway.app` em `DJANGO_ALLOWED_HOSTS`. Esse
probe verifica PostgreSQL, mas **não** monitora continuamente o serviço
após publicação; configure alertas de uptime separados.
Liveness/readiness estão isentas apenas do redirecionamento interno HTTP;
a API pública mantém obrigatoriedade de HTTPS.

Fontes:
- https://docs.railway.com/deployments/pre-deploy-command
- https://docs.railway.com/deployments/healthchecks

## Ordem do rollout

1. Aprovar região, custos e exposição (demo pública ou privada), e
   definir projeto **novo**, distinto dos projetos existentes.
2. Autorizar GitHub e preparar variáveis shared privadas.
3. Revisar `railway config plan` ou staged changes; avaliar recursos
   faturáveis, fontes, réplicas, segurança de rede e backups.
4. Apenas com aprovação: aplicar a infraestrutura. Conferir que Postgres
   e Redis sejam privados, e que os dados do Postgres sejam persistentes.
5. Garantir que a migração do Web finalize antes de liberar Worker e Beat
   para receber e processar eventos. Beat deve ter uma única instância.
6. Criar domínio público para o Web e concluir HTTPS/proxy/hosts,
   readiness e limites de segurança.
7. Executar `python scripts/smoke_deploy.py https://DOMINIO_REAL`,
   que valida GET públicos de health, schema e Swagger.
8. Fazer um teste autenticado com usuário e tickets **sintéticos**,
   verificando gravação, outbox, worker e inbox.
9. Comprovar backups restauráveis do Postgres; documentar rollback de
   código, limitação de reversão de schema e procedimento de incidentes.
10. Registrar URL, commit, logs higienizados, estado de cada serviço,
    custos aprovados e smoke real em [CHM-601 #15](https://github.com/ZaraTakion/chamados-api/issues/15).

O smoke público **não** comprova backup, worker nem autorização; a
CHM-601 só pode ser marcada Done após as evidências reais.

Consulte [runbook operacional](./OPERATIONS_RUNBOOK.md) e
[segurança de produção](./PRODUCTION_SECURITY.md).
