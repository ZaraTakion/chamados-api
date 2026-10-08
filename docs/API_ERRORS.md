# Contrato de erros da API — CHM-203

## Objetivo

Oferecer um formato previsível de erro para clientes da Chamados API sem quebrar os retornos de validação que já existiam. O handler centralizado em `chamados_api/errors.py` é registrado por `REST_FRAMEWORK["EXCEPTION_HANDLER"]`.

Esta mudança é **aditiva**. O status HTTP, cabeçalhos (incluindo `Retry-After` no HTTP 429) e campos preexistentes como `detail` e `status` permanecem. Somente respostas de **exceções tratadas pelo DRF** passam a conter também o objeto `error`. Respostas de sucesso não mudam.

## Objeto padronizado

```json
{
  "error": {
    "code": "validation_error",
    "message": "Dados inválidos.",
    "details": {
      "title": ["Este campo não pode ser em branco."]
    }
  },
  "title": ["Este campo não pode ser em branco."]
}
```

- `code`: identificador estável para clientes; não analisar texto de mensagem para decidir o comportamento.
- `message`: resumo genérico para exibição, em português.
- `details`: o retorno detalhado original do DRF, preservando campos e mensagens das validações.
- As propriedades legadas continuam no nível raiz.
- Se a exceção tiver detalhes em formato de lista em vez de dicionário, serão apresentados também em `errors`.

Os textos dos exemplos representam contratos ilustrativos. A redação exata de mensagens de bibliotecas pode variar; os códigos e o status HTTP são os sinais recomendados para clientes.

## Códigos e HTTP

| Código | HTTP usual | Situação |
| --- | --- | --- |
| `authentication_error` | 401 | JWT ausente, inválido ou expirado |
| `permission_denied` | 403 | Usuário autenticado sem direito à ação |
| `not_found` | 404 | Recurso inexistente ou oculto por isolamento de acesso |
| `validation_error` | 400 | Campo obrigatório, tipo ou escolha inválida |
| `invalid_transition` | 400 | Transição de status proibida pelo CHM-201 |
| `forbidden_field` | 400 | Campo restrito ao staff, preservando o HTTP legado |
| `method_not_allowed` | 405 | Método não permitido pela rota |
| `parse_error` | 400 | Corpo JSON malformado |
| `rate_limited` | 429 | Limite de requisições atingido |
| `api_error` | variável | Outra exceção HTTP tratada pelo DRF |

Os códigos HTTP existentes não foram alterados. Em particular, tentativas de editar `status` ou `assignee` sem permissão continuam retornando **400** pela validação do serializer; ações proibidas pelo controle de objeto, como excluir chamado sem ser staff, continuam **403**. Essa diferença de legado está documentada, não ocultada.

### Transição inválida (400)

```json
{
  "status": ["Transição de 'open' para 'resolved' não permitida."],
  "error": {
    "code": "invalid_transition",
    "message": "Transição de status não permitida.",
    "details": {"status": ["Transição de 'open' para 'resolved' não permitida."]}
  }
}
```

### Sem autenticação (401)

```json
{
  "detail": "As credenciais de autenticação não foram fornecidas.",
  "error": {
    "code": "authentication_error",
    "message": "Autenticação necessária ou inválida.",
    "details": {"detail": "As credenciais de autenticação não foram fornecidas."}
  }
}
```

### Proibido excluir (403)

```json
{
  "detail": "Somente a equipe pode excluir chamados.",
  "error": {
    "code": "permission_denied",
    "message": "Acesso negado.",
    "details": {"detail": "Somente a equipe pode excluir chamados."}
  }
}
```

## Limitações

- Somente **exceções que o DRF captura** usam este handler. Erros não tratados do Django, falhas de middleware, páginas HTML ou erros antes do pipeline DRF não são normalizados nesta entrega. Não exponha stack traces em produção.
- O handler mantém os detalhes originais já públicos; a política de mensagens detalhadas dos serializers continua sendo responsabilidade das validações de cada endpoint.
- O esquema OpenAPI pode exigir especificações de respostas de erro por operação, caso clientes desejem gerar tipagens completas do novo objeto. Este documento descreve o contrato enquanto a evolução de OpenAPI pode ser incluída em uma revisão futura.
- O código `api_error` é um fallback para outras exceções já tratadas, não significa que falhas de servidor (500) sejam capturadas pelo handler.
