# CHM-401 — Observabilidade de requisições

## Comportamento

A aplicação gera um UUIDv4 (32 caracteres hexadecimais) para cada requisição HTTP.
O identificador é retornado no cabeçalho `X-Request-ID`, permitindo correlacionar
o erro relatado por um cliente à linha correspondente nos logs JSON.
Por segurança, o servidor não utiliza IDs de correlação fornecidos pelo cliente.

Cada registro possui os campos `timestamp`, `level`, `logger`, `event` e,
quando aplicável, `request_id`, `method`, `route`, `status_code` e `duration_ms`.
A rota é o padrão definido no roteador do Django; não se registra a URL concreta.
As respostas de status 500 ou superior usam evento `http.server_error` em nível ERROR.
O tratamento público dos erros permanece inalterado.

## Privacidade

O formatador tem campos permitidos explícitos, não serializa mensagens arbitrárias
nem rastros de exceções. Não registrar dados pessoais, credenciais, corpo HTTP,
parâmetros de consulta ou cabeçalhos de clientes. A política cobre os loggers
configurados na aplicação, não necessariamente logs do proxy ou da hospedagem.

## Configuração por ambiente

Variável `APP_LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR ou CRITICAL.
O padrão no desenvolvimento é WARNING; em produção, INFO.
A saída é JSON no stderr, coletável pelo gerenciador do serviço.
Para habilitar eventos informativos no CMD, execute `set APP_LOG_LEVEL=INFO`
antes de `python manage.py runserver`.

## Verificação

Informar o `X-Request-ID` ao suporte; filtrar os logs pelo mesmo identificador.
Os testes verificam isolamento dos IDs, roteamento sem dados sensíveis,
formatação JSON, cabeçalhos e diagnósticos de erro 5xx.
Não é tracing distribuído e não substitui um sistema de diagnóstico controlado.
