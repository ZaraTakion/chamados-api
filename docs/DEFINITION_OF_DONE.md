# Definition of Done

Um issue do roadmap profissional só pode ser marcado como **Done** quando todos os itens aplicáveis abaixo estiverem satisfeitos.

## Funcionalidade

- [ ] Critérios de aceite do issue atendidos.
- [ ] Fluxo de sucesso validado.
- [ ] Principais fluxos de erro validados.
- [ ] Nenhuma mudança não relacionada foi incluída sem justificativa.

## Testes

- [ ] Novas regras possuem testes.
- [ ] Regressões relevantes possuem teste.
- [ ] `python manage.py check` passa.
- [ ] `python manage.py makemigrations --check --dry-run` passa.
- [ ] `python manage.py test` passa.
- [ ] CI está verde.

Quando a Sprint 01 implementar as ferramentas correspondentes:

- [ ] lint passa;
- [ ] cobertura não sofre queda injustificada.

## Banco de dados

Quando aplicável:

- [ ] migration é necessária e está versionada;
- [ ] rollback/impacto foi considerado;
- [ ] integridade é garantida por constraint ou regra testada;
- [ ] alteração funciona no PostgreSQL.

## Segurança

- [ ] nenhum segredo foi commitado;
- [ ] autenticação/autorização continuam corretas;
- [ ] dados sensíveis não aparecem em logs;
- [ ] inputs externos são validados;
- [ ] configuração de produção permanece segura.

## API

Quando o contrato muda:

- [ ] status HTTP faz sentido;
- [ ] schema OpenAPI foi atualizado;
- [ ] exemplos/README foram atualizados;
- [ ] compatibilidade/impacto foi considerado.

## Documentação

- [ ] README atualizado se comandos ou comportamento mudaram.
- [ ] documentação técnica atualizada se arquitetura mudou.
- [ ] limitações conhecidas registradas.
- [ ] nenhuma afirmação no README excede o que o código comprova.

## Git

- [ ] branch possui escopo único;
- [ ] commits são compreensíveis;
- [ ] diff foi revisado antes do merge;
- [ ] PR descreve problema, solução e como testar;
- [ ] `main` permanece estável após merge.

## Aprendizado

Antes de fechar um issue, o desenvolvedor deve conseguir explicar:

1. qual problema estava resolvendo;
2. por que escolheu a solução;
3. quais alternativas existiam;
4. qual trade-off foi aceito;
5. como sabe que a solução funciona.

Se a resposta para esses pontos não estiver clara, o issue ainda não está Done.
