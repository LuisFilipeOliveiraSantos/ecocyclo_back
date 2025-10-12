# 🌱 Ecocyclo Backend

[![Python](https://img.shields.io/badge/Python-3.12+-blue)](https://www.python.org/)  
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green)](https://fastapi.tiangolo.com/)  
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

Backend do projeto **Ecocyclo**, uma aplicação gamificada para incentivar o **descarte correto de lixo eletrônico** e promover a **economia circular**.

---

## ✨ Features

- **FastAPI Backend:** APIs para gestão de usuários, pontos de gamificação e registros de descarte.  
- **Gamificação:** Sistema de pontos e badges para incentivar reciclagem.  
- **Banco de Dados:** Armazena usuários, registros de descarte e conquistas.  
- **Docker:** Configuração rápida para desenvolvimento e produção.  
- **Tools:** Poetry, ruff, black, taskipy (opcional) para desenvolvimento.

---

## 📂 Estrutura do projeto

```text
ecocyclo_back/
│
├── backend/
│   ├── app/
│   │   ├── main.py          # Ponto de entrada da aplicação
│   │   ├── routers/         # Rotas da API
│   │   ├── models/          # Modelos de banco de dados
│   │   ├── schemas/         # Schemas Pydantic
│   │   ├── services/        # Regras de negócio
│   │   └── utils/           # Funções auxiliares
│   │
│   ├── tests/               # Testes automatizados
│   ├── requirements.txt     # Dependências do projeto
│   └── Dockerfile           # Configuração Docker
│
├── docker-compose.yml       # Configuração Docker para dev
├── docker-compose-prod.yml  # Configuração Docker para produção
└── .env                     # Variáveis de ambiente (não versionadas)
```

## 🚀 Getting Started
### Prerequisites

Python 3.12+ (para rodar localmente)

Docker & Docker Compose (opcional)


### Run with Docker

1. Clone o repositório:
```text
git clone https://github.com/<seu-usuario>/<seu-repositorio>.git
cd ecocyclo_back/backend
```

2. Copie e configure o arquivo .env na raiz do projeto.

Start the stack:
```
docker-compose up --build
```

3. Access API:
```
Swagger UI → http://localhost:8000/docs

ReDoc → http://localhost:8000/redoc
```
4. Check logs:
```
docker-compose logs backend db
```


### Run Locally (Backend)

1. Clone o repositório:
```
git clone https://github.com/<seu-usuario>/<seu-repositorio>.git
cd ecocyclo_back/backend
```

2. Crie e ative o ambiente virtual:
```
# Windows PowerShell
python -m venv env
.\env\Scripts\Activate.ps1

# Linux/Mac
python -m venv env
source env/bin/activate
```

3. Instale as dependências:
```
pip install -r requirements.txt
```

4. Rode o servidor FastAPI:
```
uvicorn app.main:app --reload
```

5. Access:
- API  → http://127.0.0.1:8000

- Swagger UI → http://127.0.0.1:8000/docs

- ReDoc → http://127.0.0.1:8000/redoc

## 🔧 Development Tasks

Format code:
```
task format
```

(Executa black, ruff check --fix e ruff format)

Lint:
```
task lint
```

(Executa ruff check)

Test:
```
task test
```

(Executa pytest com coverage)

Atualizar dependências:
```
pip freeze > requirements.txt
```

## 🤝 Contributing

Fork e crie uma branch:
```
git checkout -b feature/nova-funcionalidade
```

Instale dependências:
```
pip install -r requirements.txt
```

Faça commit das mudanças:
```
task format
git commit -m "feat: descrição da feature"
```

Push e crie pull request.

## 🙌 Acknowledgments

Baseado em [jonasrenault/fastapi-react-mongodb-docker](https://github.com/jonasrenault/fastapi-react-mongodb-docker)
