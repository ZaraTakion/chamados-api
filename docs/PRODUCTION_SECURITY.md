# CHM-402 — Health probes e configuração de produção

## Contrato dos endpoints

| Endpoint | Objetivo | Banco | HTTP |
| --- | --- | --- | --- |
| `GET /api/health/` | Liveness legado (compatibilidade) | Não consulta | 200 |
| `GET /api/health/live/` | Indica que o processo responde | Não consulta | 200 |
| `GET /api/health/ready/` | Confirma que o banco principal está disponível | `SELECT 1` | 200 ou 503 |

Os três endpoints são públicos. Somente os novos endpoints /live/ e /ready/
dispensam throttling para que sondas periódicas não encontrem HTTP 429.
A rota antiga /api/health/ preserva seus limites originais de requisição. Os resultados não são cacheáveis (`Cache-Control:
no-store`). O corpo mantém `status` e `timestamp`; readiness devolve
`status: unavailable` e HTTP 503 quando o banco não responde, sem informar
credenciais, host, nomes internos ou mensagens de exceções. As respostas recebem
o `X-Request-ID` configurado na CHM-401.

A readiness executa uma única consulta leve e não valida tabelas, migrations,
chamados ou conectividade com outros serviços. Liveness não deve ser
usada para tomar a decisão de distribuir tráfego se o banco estiver indisponível.

## Pré-requisitos de produção

Ao definir `DJANGO_DEBUG=false`, a aplicação recusa a inicialização
quando algum pré-requisito está ausente ou inseguro:

- `DJANGO_SECRET_KEY`: valor aleatório exclusivo, pelo menos 50 caracteres,
  sem placeholders conhecidos nem valores evidentemente repetitivos.
- `DJANGO_ALLOWED_HOSTS`: explícito e restrito aos domínios de serviço.
  O curinga `*` não é permitido.
- `DATABASE_URL`: URL de PostgreSQL persistente e gerenciado; SQLite local
  permanece disponível para desenvolvimento.
- `DJANGO_SECURE_SSL_REDIRECT`: deve permanecer habilitado em produção.
- Cookies de sessão e CSRF usam `Secure`; o Django ativa proteção de tipo
  MIME e referrer policy.

Para gerar uma chave aleatória em um terminal seguro, sem colocá-la em
código-fonte: `python -c "from django.core.management.utils import
get_random_secret_key; print(get_random_secret_key())"`. Salve-a somente em
um gerenciador de segredos ou variável protegida.

Quando o HTTPS é terminado por proxy, habilite
`DJANGO_TRUST_PROXY_SSL_HEADER=true` **somente** se o proxy estiver configurado
para remover o cabeçalho de protocolo recebido do cliente e substituir por seu
próprio valor confiável. Caso contrário, deixe desabilitado. Um proxy mal
configurado permite falsificação de conexão HTTPS. Sem configuração adequada,
`SECURE_SSL_REDIRECT` pode causar redirecionamentos em loop.

## Checklist operacional antes do deploy

1. Garantir TLS, domínio e proxy reverso corretamente configurados.
2. Usar variáveis e segredos privados específicos do ambiente; nunca usar
   o `.env.example` diretamente em produção.
3. Executar `python manage.py check --deploy` com as variáveis finais e
   analisar os warnings de segurança, incluindo a decisão de HSTS.
4. Garantir PostgreSQL com backup, monitoramento e migrations aplicadas.
5. Usar /api/health/live/ para reinício de processos e /api/health/ready/
   para decisão de tráfego.
6. Conferir logs JSON, correlação e ausência de dados sensíveis.
7. Executar smoke tests reais depois da publicação e configurar alarmes.

Os testes automatizados verificam liveness sem dependência de banco,
readiness com banco saudável/indisponível, resposta 503 segura, consulta
mínima, exposição no OpenAPI e rejeição de configurações inseguras.

## Limitações

Testes locais/CI não garantem confiabilidade do serviço em produção. A
política de backup, observabilidade de infraestrutura, teste TLS/HSTS no
domínio final, rotação de segredos e configuração segura do proxy dependem
do operador no ambiente de implantação. A URL de readiness é pública e não
divulga a causa interna de falhas.

## CHM-601 — Hospedagem Railway

O [guia de deploy](./DEPLOY_RAILWAY.md) documenta três processos separados
(Web, Celery Worker e Beat) e bancos privados. O Web executa a migration
em pre-deploy; `/api/health/ready/` serve como gate de tráfego. Apenas os
endpoints públicos de health (live/ready) têm isenção do redirecionamento
HTTP para permitir sondas internas do Railway, sem conteúdo sensível. O
restante da API deve continuar forçando HTTPS. Consulte também o
[runbook operacional](./OPERATIONS_RUNBOOK.md) antes da publicação.

`DJANGO_HSTS_SECONDS` começa em zero, pois HSTS deve ser ativado apenas
após certificar o HTTPS e o domínio final. Variáveis de segredos são
configuradas no provedor, nunca no Git. Os arquivos do `deploy/` são
preparação de infraestrutura, **não evidência de site já publicado**.
