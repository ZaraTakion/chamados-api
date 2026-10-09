# Usando a coleção Postman — Chamados API Local Demo

Arquivo: [`postman/Chamados-API-Local-Demo.postman_collection.json`](../postman/Chamados-API-Local-Demo.postman_collection.json)

## Segurança e ambiente

A coleção é importável como Postman v2.1 e inclui **18 requisições**
agrupadas em saúde, JWT, chamados e notificações. Não contém tokens,
senhas reais nem endereços externos; o valor `baseUrl` é
`http://127.0.0.1:8000`.

- Execute a API localmente conforme [LOCAL_DEMO.md](./LOCAL_DEMO.md).
- Importe a coleção usando **Import** no Postman.
- Em **Variables**, defina `requesterUsername` / `requesterPassword`
  e `staffUsername` / `staffPassword` **somente no seu ambiente local**.
  Use contas sintéticas. A coleção deixa essas variáveis vazias.
- Rode as requisições de login e copie **somente no Postman local** o valor
  `access` para `requesterAccessToken` ou `staffAccessToken`.
  Para não sincronizar segredos, evite equipes compartilhadas e
  **limpe esses valores após a demonstração**. Não exporte a coleção
  novamente com valores preenchidos.
- Nunca compartilhe a aba **Code / cURL** autenticada, logs Postman,
  refresh tokens ou capturas com informações de credenciais.

## Ordem sugerida

1. `01 — Saúde e documentação`: liveness, readiness e OpenAPI.
2. `02 — Identidade JWT`: registro **uma única vez** (o nome deve ser
   único), login solicitante e login de equipe com `is_staff=True`,
   perfil autenticado.
3. `03 — Chamados`: criar (HTTP 201), listar, consultar, mudar
   status como equipe, comentar e consultar histórico. A criação grava
   automaticamente `ticketId` e `ticketReference` na coleção.
4. Em outro CMD, execute
   `python manage.py process_notifications --watch --interval 10`.
5. `04 — Notificações privadas`: equipe deve consultar a inbox
   (HTTP 200, array `results`), solicitante vê somente seus avisos,
   e acesso sem JWT retorna HTTP 401.

## Resultados e limitações

A coleção tem checagens básicas de status e formato, mas não substitui
a suíte Django nem prova um deploy em produção. A ordem e os estados
dos tickets influenciam alterações. Ao repetir a coleção, crie contas
novas ou pule o registro para evitar conflitos de usuário já existente.

**Não use** a URL `http://0.0.0.0` nem exponha `runserver` para
redes externas. Para evidências reproduzíveis sem senhas reais use o
[teste end-to-end automatizado](../tickets/tests/test_local_demo_e2e.py).
