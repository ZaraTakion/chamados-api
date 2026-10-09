# CHM-601 — Preview HTTPS privado sem mensalidade (Cloudflare)

**Status:** código integrado e [CI 6/6 jobs aprovado](https://github.com/ZaraTakion/chamados-api/actions/runs/37948905306). **URL externa ainda não ativada nem verificada**; isso depende de executar o script no Windows.

Este modo cria uma **demonstração temporária, protegida por PIN de e-mail**
via Cloudflare Quick Tunnel. Não contrata servidor, domínio, serviço Railway,
PostgreSQL gerenciado nem Redis. **Não é deploy 24/7 nem produção.**

A Cloudflare introduziu em 02/10/2026 a opção `--allowed-mail` a partir
do `cloudflared` **2026.9.3**. Quick Tunnels sem esse argumento são
acessíveis a qualquer pessoa que conheça a URL; por isso, **nosso script
se recusa a iniciar** sem um e-mail individual e uma versão atual.

Documentação oficial:
- https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/
- https://developers.cloudflare.com/changelog/post/2026-10-02-protected-quick-tunnels/
- https://developers.cloudflare.com/tunnel/downloads/

## O que fica protegido

A execução do script [`scripts/protected_preview.py`](../scripts/protected_preview.py)
cria três processos gerenciados na própria máquina:

1. **Cloudflare Quick Tunnel**, sempre com `--allowed-mail`: exige
   verificação de posse do e-mail via PIN do Cloudflare Access. A URL HTTPS
   é aleatória e deixa de funcionar após encerrar o processo.
2. **Waitress**, servidor WSGI Python compatível com Windows, vinculado
   **somente a `127.0.0.1:8765`**, dois threads. Diferentemente do
   `runserver`, não oferece uma página de debug de desenvolvimento.
   Confia no cabeçalho de protocolo apenas da conexão local do proxy.
3. **Processador Django** de notificação, executado no processo separado
   e apontado apenas para a base temporária.

Além disso, o script configura automaticamente no processo:

- `DJANGO_DEBUG=false`, segredo aleatório efêmero exclusivo e
  `DJANGO_ALLOWED_HOSTS` **exatamente igual** ao subdomínio criado.
- Redirecionamento obrigatório para HTTPS nos endpoints normais.
- Banco isolado em `data/protected-preview.sqlite3`, nunca
  `data/db.sqlite3`. Não reutiliza contas, tickets, tokens nem senhas
  da sua base local existente. O caminho e o uso de SQLite são
  validados de forma explícita; esse modo não relaxa os requisitos do
  deployment de produção.
- `migrate` e `collectstatic` antes de disponibilizar o servidor.
- Desligamento coordenado de tunnel, servidor e processador com
  `Ctrl+C`.

O segredo muda a cada sessão: JWT e sessões anteriores deixam de
funcionar quando a demonstração é reiniciada. O SQLite isolado pode
permanecer entre sessões, mas seus dados devem ser **exclusivamente
sintéticos**. Para começar de novo, pare todos os processos e apague
somente `data/protected-preview.sqlite3`, se não precisar dos dados de
teste. **Nunca** apague seu `data/db.sqlite3` original.

## Primeiro uso no Windows

1. Instale ou atualize `cloudflared` usando a opção oficial para
   Windows em https://developers.cloudflare.com/tunnel/downloads/ .
   Ele precisa estar disponível no PATH como `cloudflared.exe`.
   **Não instalar como serviço do Windows nem configurar port forwarding.**
2. No projeto já sincronizado com a `main`, ative a `.venv` e instale
   as dependências de desenvolvimento, incluindo Waitress:

   ```bat
   python -m pip install -r requirements-dev.txt
   cloudflared --version
   ```

3. Com o seu **e-mail real privado** no próprio CMD (não envie o endereço
   nem o PIN nesta conversa), execute:

   ```bat
   python scripts/protected_preview.py --allowed-mail voce@exemplo.com
   ```

4. O script fornece um endereço temporário no formato
   `https://nome-aleatorio.trycloudflare.com`. Abra-o no navegador:
   a Cloudflare pedirá o e-mail autorizado e enviará um PIN.
   Em seguida abra `/api/docs/` na mesma URL e use Swagger.
   O destinatário não precisa criar conta Cloudflare.
5. Use `POST /api/auth/register/` para criar um solicitante fictício,
   e `POST /api/auth/token/` para autenticar. Para testar o staff,
   crie um superusuário **somente no banco isolado** por um comando
   rodando sob o mesmo ambiente protegido, ou use os testes
   automatizados do repositório como evidência.
6. Quando terminar, **`Ctrl+C`** na janela do preview encerra
   todos os serviços e revoga o acesso à URL antiga.

**Importante:** o script **não** pode transferir credenciais entre
processos ou contas. O superusuário criado no banco local original não
aparece na base isolada do preview. Em uma demo remota é suficiente
mostrar as rotas, o cadastro e tickets de teste; a entrega privada de
notificações já está coberta por testes E2E automatizados.

## Critérios de aceite e segurança

- Só iniciar se `cloudflared >= 2026.9.3`, 1–3 e-mails individuais
  explícitos, host sob `trycloudflare.com`, DEBUG falso,
  segredo forte e SQLite isolado. Falhar fechado caso contrário.
- Nenhuma porta de rede no roteador; Waitress somente no loopback;
  não compartilhar endereço publicamente, e-mail, PIN, JWT ou senhas.
- Autenticação por e-mail protege o *acesso ao site*, e o JWT continua
  exigido pela API. Evite usuários reais e dados pessoais.
- **Não executar outro worker local ou Celery** na base isolada.
- O HTTPS existe entre navegador e Cloudflare; a conexão local de
  `cloudflared` até Waitress é HTTP restrito ao loopback.
- Quick Tunnels são **temporários**, URL não é estável, não possuem SLA
  e não aceitam clientes não-interativos sem sessão autenticada.
  Postman/cURL sem interação de navegador não são o mecanismo de
  demonstração remota recomendado.
- A CHM-601 **não** estará completa como produção. Falta disponibilidade
  permanente, PostgreSQL/Redis hospedados, backups remotos, monitoramento
  e teste HTTPS num serviço realmente implantado.

## Verificação automática

O CI valida a configuração, o isolamento e a exigência de e-mail,
incluindo teste `DEBUG=False` com SQLite **exclusivamente** quando
`DJANGO_PROTECTED_PREVIEW=true` e hostname exato. Esses testes não
iniciam túnel nem expõem banco. A validação externa real exige que o
script seja executado na máquina do proprietário, com uma lista de
e-mails autorizados escolhida por ele.

```bat
python manage.py test tickets.tests.test_protected_tunnel
```

## Aceite técnico registrado — 09/10/2026

- [PR #32 integrada](https://github.com/ZaraTakion/chamados-api/pull/32), commit `9444dfaf`.
- PostgreSQL: **143 testes aprovados**; SQLite 3 versões Python: **142 aprovados + 1 skip**; cobertura **93,7%**; seis jobs verdes.
- Smoke real de Waitress no GitHub Actions (loopback): hostname correto/HTTPS aceitos, redirecionamento HTTP normal e Host indevido rejeitado.
- Ainda **não** há URL `trycloudflare.com` testada nem confirmação de PIN com e-mail em um navegador externo. O script foi construído e testado, **não executado na máquina do proprietário**.
- Os critérios originais de produção da CHM-601 continuam pendentes.
