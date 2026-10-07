# Chamados API

API REST para abrir e acompanhar solicitações de suporte. Construída com Django REST Framework, autenticação JWT e banco relacional. O ambiente local usa SQLite; o Docker Compose oferece PostgreSQL com volume persistente.

## Funcionalidades

- Cadastro de solicitante, login JWT, renovação e revogação de refresh token.
- Perfil do usuário autenticado.
- Criação e acompanhamento dos próprios chamados.
- Fila de atendimento para equipe (`is_staff`), com atribuição, mudanças de status e exclusão.
- Prioridade, categoria, busca, filtros, ordenação e paginação.
- Conversa por chamado, com notas internas visíveis somente à equipe.
- Validação de dados, limite básico de requisições anônimas e documentação OpenAPI.

## Executar localmente com SQLite

Requer Python 3.10 ou superior.

```bash
git clone https://github.com/ZaraTakion/chamados-api.git
cd chamados-api
python -m venv .venv
```

Ative o ambiente virtual e instale as dependências:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate

python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

A API fica em `http://127.0.0.1:8000`; documentação interativa em `/api/docs/` e administração Django em `/admin/`. O arquivo local SQLite é criado em `data/db.sqlite3` e não é versionado.

## Executar com Docker e PostgreSQL

```bash
cp .env.example .env
docker compose up --build
```

O Compose executa as migrações, inicia a API em `http://localhost:8000` e mantém o banco no volume `postgres_data`. Os valores de `.env.example` servem apenas para desenvolvimento local. Em produção, use segredo aleatório privado, credenciais individuais, `DJANGO_DEBUG=false`, hosts explícitos, TLS e backups do banco.

Também é possível apontar a aplicação para um PostgreSQL gerenciado definindo `DATABASE_URL`. Em hospedagem com disco efêmero, não dependa do SQLite local: use PostgreSQL ou outro armazenamento persistente.

## Autenticação

Cadastre um usuário:

```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"ana","email":"ana@example.com","password":"Senha-forte-2026!"}'
```

Solicite tokens (OAuth2 password form, campos `username` e `password`):

```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=ana&password=Senha-forte-2026%21"
```

Envie o token de acesso em chamadas protegidas: `Authorization: Bearer <access>`. Acesso expira em 20 minutos; refresh em 1 dia. Renovação: `POST /api/auth/token/refresh/` com `{"refresh":"..."}`. Revogação: `POST /api/auth/token/blacklist/` com o refresh token. Não armazene tokens em logs ou repositórios.

## Rotas principais

| Método | Rota | Acesso | Descrição |
|---|---|---|---|
| `GET` | `/api/health/` | Público | Estado da API |
| `POST` | `/api/auth/register/` | Público, limitado | Criar conta de solicitante |
| `POST` | `/api/auth/token/` | Público, limitado | Obter tokens JWT |
| `POST` | `/api/auth/token/refresh/` | Refresh token | Renovar access token |
| `POST` | `/api/auth/token/blacklist/` | Refresh token | Revogar refresh token |
| `GET` | `/api/auth/me/` | Autenticado | Perfil atual |
| `GET`, `POST` | `/api/tickets/` | Autenticado | Listar/criar chamados |
| `GET`, `PUT`, `PATCH`, `DELETE` | `/api/tickets/{id}/` | Dono ou equipe | Consultar/alterar chamado; exclusão só pela equipe |
| `GET`, `POST` | `/api/tickets/{id}/comments/` | Dono ou equipe | Listar/comentar; notas internas só para equipe |
| `GET` | `/api/schema/` | Público | Esquema OpenAPI |
| `GET` | `/api/docs/` | Público | Swagger UI |

Estados: `open`, `in_progress`, `waiting`, `resolved`, `closed`. Prioridades: `low`, `normal`, `high`, `urgent`. A equipe é composta por usuários marcados como `is_staff` no Django Admin; a criação pública nunca concede esse privilégio.

Listas são paginadas (20 itens). Filtros e busca podem ser combinados, por exemplo: `/api/tickets/?status=open&priority=high&search=login&ordering=-created_at&page=1`.

Exemplo de criação de chamado, após substituir `<access>` por um access token válido:

```bash
curl -X POST http://127.0.0.1:8000/api/tickets/ \
  -H "Authorization: Bearer <access>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Acesso bloqueado","description":"Não consigo entrar na minha conta.","category":"Acesso","priority":"high"}'
```

Para promover um usuário existente a integrante da equipe, entre em `/admin/` com o superusuário e marque `Staff status`. Não conceda esse perfil para contas públicas.

## Configuração

- `DJANGO_SECRET_KEY`: segredo Django; obrigatório quando `DJANGO_DEBUG=false`.
- `DJANGO_DEBUG`: padrão local `true`; em produção defina `false`.
- `DJANGO_ALLOWED_HOSTS`: hosts permitidos separados por vírgula.
- `DATABASE_URL`: URL PostgreSQL opcional; sem ela, usa SQLite local.
- `SQLITE_PATH`: caminho alternativo do arquivo SQLite.
- `DJANGO_SECURE_SSL_REDIRECT`: redireciona para HTTPS quando `DEBUG=false` (padrão `true`).

## Testes e verificações

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Os testes cobrem cadastro, autenticação, isolamento por usuário, fluxo da equipe, comentários internos, filtros e documentação. O GitHub Actions executa essas verificações em Python 3.10, 3.11 e 3.12.


## Roadmap profissional

A próxima fase do projeto está planejada em Scrum para transformar esta API em uma evidência mais completa de engenharia de backend.

**Estado atual:** planejamento concluído; implementação aguardando a conclusão do projeto Bird.

- [Status atual](docs/STATUS.md)
- [Scrum e sprints](docs/SCRUM.md)
- [Roadmap de 90 dias](docs/ROADMAP.md)
- [Trilha de estudos](docs/LEARNING_PATH.md)
- [Definition of Done](docs/DEFINITION_OF_DONE.md)
- [Backlog no GitHub Issues](https://github.com/ZaraTakion/chamados-api/issues)

A implementação seguirá WIP limitado: **uma tarefa Doing por vez**.
