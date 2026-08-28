
# API E-commerce

Backend da aplicação de e-commerce desenvolvido com **FastAPI**, **SQLAlchemy** e **PostgreSQL**.

O gerenciamento do ambiente virtual e das dependências é realizado utilizando **uv**.

## Tecnologias

* Python 3.14+
* FastAPI
* SQLAlchemy
* PostgreSQL
* Psycopg 3
* Alembic
* Pydantic Settings
* python-dotenv
* uv

---

## Estrutura do projeto

```text
API_Ecommerce/
│
├── alembic/
│   └── versions/
│
├── src/
│   └── api_ecommerce/
│       ├── controllers/
│       ├── core/
│       ├── database/
│       ├── models/
│       ├── routers/
│       ├── schemas/
│       └── main.py
│
├── tests/
│
├── .env
├── .gitignore
├── .python-version
├── alembic.ini
├── pyproject.toml
├── README.md
└── uv.lock
```

### Organização

| Diretório       | Responsabilidade                                      |
| ---------------- | ----------------------------------------------------- |
| `controllers/` | Regras e operações relacionadas aos recursos        |
| `core/`        | Configurações e componentes centrais da aplicação |
| `database/`    | Configuração e conexão com o banco de dados        |
| `models/`      | Models do SQLAlchemy                                  |
| `routers/`     | Rotas da API                                          |
| `schemas/`     | Schemas do Pydantic                                   |
| `tests/`       | Testes automatizados                                  |
| `alembic/`     | Migrations do banco de dados                          |

---

# Pré-requisitos

Antes de executar o projeto, tenha instalado:

* **Python 3.14 ou superior**
* **PostgreSQL**
* **Git**
* **uv**

Verifique as instalações:

```bash
python --version
```

```bash
uv --version
```

```bash
psql --version
```

```bash
git --version
```

---

# Instalação

## 1. Clonar o repositório

```bash
git clone <URL_DO_REPOSITORIO>
```

Entre na pasta do projeto:

```bash
cd API_Ecommerce
```

---

## 2. Instalar as dependências

O projeto utiliza o **uv** para gerenciamento das dependências.

Execute:

```bash
uv sync
```

O comando irá criar o ambiente virtual e instalar as dependências definidas no `pyproject.toml`.

O projeto possui um arquivo `uv.lock`, que deve ser mantido no repositório para garantir versões consistentes das dependências.

---

# Configuração do PostgreSQL

O projeto utiliza **PostgreSQL** como banco de dados.

Antes de executar a API, é necessário criar o banco de dados.

Por exemplo:

```sql
CREATE DATABASE ecommerce;
```

Você pode executar esse comando utilizando o `psql` ou uma ferramenta como o **pgAdmin**.

---

# Configuração do `.env`

Na raiz do projeto existe um arquivo `.env`.

Configure a conexão com o PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://postgres:SENHA@localhost:5432/ecommerce
```

Exemplo:

```env
DATABASE_URL=postgresql+psycopg://postgres:123456@localhost:5432/ecommerce
```

A URL segue o seguinte formato:

```text
postgresql+psycopg://USUARIO:SENHA@HOST:PORTA/BANCO
```

Onde:

* `USUARIO` → usuário do PostgreSQL;
* `SENHA` → senha do PostgreSQL;
* `HOST` → endereço do servidor;
* `PORTA` → porta do PostgreSQL, normalmente `5432`;
* `BANCO` → nome do banco de dados.

> **Importante:** nunca envie informações reais de acesso ao banco para o GitHub.

O `.env` deve estar no `.gitignore`:

```gitignore
.env
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
```

---

# Migrations

O projeto utiliza **Alembic** para controlar as alterações na estrutura do banco de dados.

Depois de configurar o PostgreSQL e o `.env`, execute:

```bash
uv run alembic upgrade head
```

Esse comando aplica todas as migrations existentes.

## Criar uma migration

Depois de alterar algum model do SQLAlchemy:

```bash
uv run alembic revision --autogenerate -m "descricao_da_alteracao"
```

Exemplo:

```bash
uv run alembic revision --autogenerate -m "adiciona telefone ao usuario"
```

Depois aplique a migration:

```bash
uv run alembic upgrade head
```

## Verificar a migration atual

```bash
uv run alembic current
```

## Ver histórico das migrations

```bash
uv run alembic history
```

---

# Executando a API

Com as dependências instaladas e o banco configurado:

```bash
uv run uvicorn api_ecommerce.main:app --reload
```

A API será executada, por padrão, em:

```text
http://localhost:8000
```

O parâmetro `--reload` faz com que o servidor seja reiniciado automaticamente após alterações no código.

---

# Documentação

O FastAPI disponibiliza documentação automática.

## Swagger

Acesse:

```text
http://localhost:8000/docs
```

## ReDoc

Acesse:

```text
http://localhost:8000/redoc
```

---

# Testes

Os testes estão localizados no diretório:

```text
tests/
```

Para executá-los:

```bash
uv run pytest
```

Para obter informações detalhadas:

```bash
uv run pytest -v
```

---

# Dependências

As principais dependências do projeto são:

```toml
fastapi[standard]
pydantic-settings
sqlalchemy
psycopg[binary]
python-dotenv
alembic
```

### FastAPI

Framework utilizado para desenvolvimento da API REST.

### SQLAlchemy

ORM utilizado para comunicação entre a aplicação e o PostgreSQL.

### Psycopg

Driver utilizado pelo SQLAlchemy para conexão com o PostgreSQL.

O projeto utiliza o **Psycopg 3** com suporte `binary`.

### Alembic

Ferramenta utilizada para gerenciamento das migrations do banco de dados.

### Pydantic Settings

Utilizado para gerenciamento das configurações da aplicação e variáveis de ambiente.

### python-dotenv

Utilizado para carregamento de variáveis de ambiente através do arquivo `.env`.

---

# Principais comandos

### Instalar dependências

```bash
uv sync
```

### Adicionar uma dependência

```bash
uv add <pacote>
```

Exemplo:

```bash
uv add httpx
```

### Remover uma dependência

```bash
uv remove <pacote>
```

### Executar a API

```bash
uv run uvicorn api_ecommerce.main:app --reload
```

### Executar migrations

```bash
uv run alembic upgrade head
```

### Criar migration

```bash
uv run alembic revision --autogenerate -m "descricao"
```

### Executar testes

```bash
uv run pytest
```

---

# Integração com o Frontend

O backend é consumido pelo frontend desenvolvido em **Next.js**.

Durante o desenvolvimento, a arquitetura funciona da seguinte maneira:

```text
┌─────────────────────────────┐
│          Frontend            │
│           Next.js            │
│                             │
│     http://localhost:3000   │
└──────────────┬──────────────┘
               │
               │ HTTP / REST
               ▼
┌─────────────────────────────┐
│           Backend            │
│           FastAPI            │
│                             │
│     http://localhost:8000   │
└──────────────┬──────────────┘
               │
               │ SQL
               ▼
┌─────────────────────────────┐
│         PostgreSQL           │
│                             │
│      localhost:5432         │
└─────────────────────────────┘
```

---

# CORS

Durante o desenvolvimento, o backend deve permitir requisições provenientes do frontend.

A origem utilizada pelo frontend é:

```text
http://localhost:3000
```

Caso o frontend seja executado em outra porta ou endereço, a configuração de CORS deverá ser ajustada.

---

# Execução completa

Para executar o projeto em uma máquina nova:

### 1. Clonar o projeto

```bash
git clone <URL_DO_REPOSITORIO>
```

### 2. Entrar na pasta

```bash
cd API_Ecommerce
```

### 3. Instalar as dependências

```bash
uv sync
```

### 4. Criar o banco PostgreSQL

```sql
CREATE DATABASE ecommerce;
```

### 5. Configurar o `.env`

```env
DATABASE_URL=postgresql+psycopg://postgres:SENHA@localhost:5432/ecommerce
```

### 6. Aplicar as migrations

```bash
uv run alembic upgrade head
```

### 7. Iniciar a API

```bash
uv run uvicorn api_ecommerce.main:app --reload
```

### 8. Acessar o Swagger

```text
http://localhost:8000/docs
```

---

# 9.Projeto

Projeto acadêmico de desenvolvimento de uma aplicação de e-commerce.
