# CHM-602 — Checklist de aceite para release local

**Escopo:** `v1.0.0-local.1`, **pré-release de desenvolvimento
local**. Não é deploy de produção.

## Itens realizados na preparação (sujeitos ao CI da PR)

- [x] Backend e modelo de permissões documentados em `README.md`.
- [x] Guia de reprodução no Windows em `docs/LOCAL_DEMO.md`.
- [x] Coleção Postman com 18 requisições, sem credenciais armazenadas.
- [x] Arquitetura local e alternativa Docker ilustradas.
- [x] Notas de versão, CHANGELOG, case de portfólio.
- [x] Teste end-to-end sintético com JWT, chamados e inbox privada.
- [x] CI Python 3.10/3.11/3.12 + PostgreSQL + Redis/Celery.
- [x] Evidências manuais sanitizadas: HTTP 201 e outbox/inbox SQLite.
- [x] Workflow preparado para captura de screenshot **real** e pré-release
  com tag somente após passar CI.

## Critérios a comprovar no commit/tag final

- [x] CI da PR de documentação/release todo verde ([execução 37879092847](https://github.com/ZaraTakion/chamados-api/actions/runs/37879092847), seis jobs).
- [x] Screenshot Swagger gerado por Chrome e disponível como artefato `swagger-ci-capture` (GitHub Actions 37879092847).
- [x] PR CHM-602 [#31](https://github.com/ZaraTakion/chamados-api/pull/31) integrada na `main` (commit `7da98d7`).
- [ ] CI do commit de publicação verde.
- [ ] Tag `v1.0.0-local.1` publicada e asset PNG real na GitHub Release.
- [ ] Link da release registrado no README/Issue e status atualizado.

## Desvios conscientes em relação à DoD original

- **Deploy HTTPS público:** **não realizado**. O usuário não autorizou
  hospedagem paga; a CHM-601 permanece aberta. Não marcar como aprovado.
- **Smoke de produção:** **não realizado**. Substituição explícita para a
  release local: smoke HTTP no Docker CI e fluxo JWT completo com dados
  sintéticos, além da demonstração em SQLite no Windows.
- **Link de demo pública:** **não existe**. Portfólio aponta para
  repositório, release, documentação e evidências de CI; para executar,
  outra pessoa segue `docs/LOCAL_DEMO.md`.
- **GET da inbox no navegador pessoal:** não observado. Comportamento
  validado via teste real HTTP/JWT em ambiente de CI.

A versão `local.1` pode ser divulgada de forma profissional e honesta;
não é apropriado afirmar que a Definition of Done **de produção** foi
integralmente cumprida. A pré-release informa expressamente isso.

## Pedido de publicação

A partir desta revisão aprovada, o commit com mensagem
`release: v1.0.0-local.1` aciona no GitHub Actions a criação da
pré-release após executar novamente os jobs de qualidade e integração.
Não é executado deploy externo e nenhum segredo de usuário é acessado.
