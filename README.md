<div align="center">

# 🚀 AI-Powered Blog Backend

### A production-oriented FastAPI backend showcasing modern backend engineering and AI integration.

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-316192?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge)](https://www.sqlalchemy.org/)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

---

## 📖 About

This project is my primary backend engineering portfolio project.

Instead of focusing on a basic CRUD application, this backend explores production-oriented architecture while integrating modern AI services.

The goal is to build software the same way production backends are designed—using clean architecture, asynchronous programming, structured logging, centralized exception handling, reusable services, and scalable API design.

---

# ✨ Features

### 🤖 AI Services

- AI Content Rephrasing
- AI Title Generation
- AI Text Summarization
- AI Sentiment Analysis
- AI Intent Classification

### 🔐 Authentication

- JWT Authentication
- OAuth2 Bearer Tokens
- Password Hashing

### ⚙ Backend Engineering

- Async FastAPI
- PostgreSQL
- SQLAlchemy Async ORM
- Alembic Migrations
- Pydantic Validation
- Dependency Injection
- Structured Logging
- Centralized Exception Handling
- Consistent API Response Wrapper

---

# 🏗 Architecture

```text
                Client
                   │
                   ▼
           FastAPI Routes
                   │
                   ▼
          Business Services
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   Database Layer         AI Services
        │                     │
        ▼                     ▼
 PostgreSQL              Large Language Model
```

---

# 📂 Project Structure

```text
.
├── Ai/
├── core/
├── db_tables/
├── migrations/
├── routers/
│   ├── ai/
│   ├── auth/
│   ├── posts/
│   └── users/
├── utils/
│   ├── logging/
│   ├── schemas.py
│   ├── hashing.py
│   └── ...
├── main.py
└── requirements.txt
```

---

# 🛠 Tech Stack

| Category | Technologies |
|----------|--------------|
| Backend | FastAPI |
| Language | Python |
| Database | PostgreSQL |
| ORM | SQLAlchemy (Async) |
| Authentication | JWT, OAuth2 |
| Validation | Pydantic |
| AI | LangChain, Groq |
| HTTP Client | HTTPX |
| Database Migration | Alembic |

---

# 🚀 Getting Started

### Clone the repository

```bash
git clone https://github.com/Floats-del/blog-ai-service-developing.git
```

---

### Create a virtual environment

```bash
python -m venv .venv
```

---

### Activate it

Windows

```bash
.venv\Scripts\activate
```

Linux

```bash
source .venv/bin/activate
```

---

### Install dependencies

```bash
pip install -r requirements.txt
```

---

### Configure environment variables

Create a `.env` file.

```env
DATABASE_URL=

HASH_SECRET_KEY=

ALGORITHM=

ACCESS_TOKEN_EXPIRE_MINUTES=

GROQ_API_KEY=

LANGSMITH_API_KEY=
```

---

### Apply database migrations

```bash
alembic upgrade head
```

---

### Start the server

```bash
uvicorn main:app --reload
```

---

# 📈 Current Engineering Focus

This project is continuously evolving toward production-quality backend architecture.

Current areas of focus include:

- Clean Architecture
- AI Service Design
- Better Logging
- Performance Improvements
- Authentication
- Error Handling

---

# 🗺 Roadmap

- ✅ Async FastAPI
- ✅ JWT Authentication
- ✅ PostgreSQL Integration
- ✅ AI Services
- ✅ Structured Logging
- ✅ Separation of Concerns
- ⏳ Redis Caching
- ⏳ JWT Session Revocation
- ⏳ Docker
- ⏳ Background Workers
- ⏳ API Gateway / BFF
- ⏳ CI/CD Pipeline

---

# 📜 License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for more information.