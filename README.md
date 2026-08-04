<div align="center">

# 🚀 AI-Powered Blog Backend

### A production-oriented FastAPI backend demonstrating scalable backend engineering, AI integration, distributed task processing, and modern infrastructure.

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge\&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?style=for-the-badge\&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-316192?style=for-the-badge\&logo=postgresql)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge)](https://www.sqlalchemy.org/)
[![Redis](https://img.shields.io/badge/Redis-7.0-DC382D?style=for-the-badge\&logo=redis)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5.x-37814A?style=for-the-badge\&logo=celery)](https://docs.celeryq.dev/)
[![Nginx](https://img.shields.io/badge/Nginx-Reverse%20Proxy-009639?style=for-the-badge\&logo=nginx)](https://nginx.org/)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

## 📖 About

This project is my primary backend engineering portfolio project.

Rather than focusing on a basic CRUD application, this backend explores production-style software architecture while integrating modern AI capabilities.

The project emphasizes scalable backend design through asynchronous programming, service-layer architecture, distributed background workers, structured logging, centralized exception handling, authentication, caching, and AI orchestration.

## ✨ Features

### 🤖 AI Services

* AI Content Rephrasing
* AI Title Generation
* AI Text Summarization
* AI Sentiment Analysis
* AI Intent Classification
* Structured LLM Outputs
* AI Output Recovery Pipeline

### 🔐 Authentication & Security

* JWT Authentication
* OAuth2 Bearer Tokens
* Password Hashing
* Redis-backed Session Management
* Session Revocation
* Logout From All Devices
* User Ban System
* Protected Endpoints

### ⚙ Backend Engineering

* Async FastAPI
* PostgreSQL
* SQLAlchemy Async ORM
* Alembic Migrations
* Dependency Injection
* Service Layer Architecture
* Centralized Exception Handling
* Standardized API Responses
* Structured Logging

### ⚡ Infrastructure

* Redis Caching
* Redis Session Storage
* Celery Background Workers
* Async AI Task Processing
* Task Status Tracking
* SlowAPI Rate Limiting
* Nginx Reverse Proxy

## 🏗 High-Level Architecture

```text
                        Client
                           │
                           ▼
                   Nginx Reverse Proxy
                           │
                           ▼
                    FastAPI Application
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
 Authentication        AI Gateway      Business Services
        │                  │                  │
        ▼                  ▼                  ▼
 Redis Sessions      Celery Queue      PostgreSQL
 Redis Cache             │
                          ▼
                   AI Background Workers
                          │
                          ▼
                     Groq / LangChain
```

## 🧠 AI Processing Flow

```text
Client
   │
   ▼
POST /title_gen
   │
   ▼
Authentication
   │
   ▼
Quota Reservation
   │
   ▼
Celery Queue
   │
   ▼
AI Worker
   │
   ▼
Groq / LangChain
   │
   ▼
Redis Result Backend
   │
   ▼
GET /title_gen/{task_id}
```

## 📂 Project Structure

```text
.
├── Ai/
├── celery_worker/
│   ├── celery_app.py
│   └── tasks/
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
│   └── ...
├── main.py
└── requirements.txt
```

## 🛠 Tech Stack

| Category            | Technologies     |
| ------------------- | ---------------- |
| Backend             | FastAPI          |
| Language            | Python 3.12      |
| Database            | PostgreSQL       |
| ORM                 | SQLAlchemy Async |
| Authentication      | JWT, OAuth2      |
| AI                  | LangChain, Groq  |
| AI Monitoring       | LangSmith        |
| Cache               | Redis            |
| Background Jobs     | Celery           |
| Rate Limiting       | SlowAPI          |
| Reverse Proxy       | Nginx            |
| Validation          | Pydantic         |
| Database Migrations | Alembic          |
| HTTP Client         | HTTPX            |

## 🚀 Getting Started

Clone the repository

```bash
git clone https://github.com/Floats-del/blog-ai-service-developing.git
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate it

Windows

```bash
.venv\Scripts\activate
```

Linux

```bash
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
DATABASE_URL=

HASH_SECRET_KEY=

ALGORITHM=

ACCESS_TOKEN_EXPIRE_MINUTES=

GROQ_API_KEY=

LANGSMITH_API_KEY=
```

Run migrations

```bash
alembic upgrade head
```

Start Redis

```bash
redis-server
```

Start Celery

```bash
celery -A celery_worker.celery_app:celery_app worker --loglevel=info
```

Start FastAPI

```bash
uvicorn main:app --reload
```

## 📈 Current Engineering Focus

* Distributed Background Processing
* AI Service Orchestration
* Scalable Authentication
* Backend Observability
* Performance Optimization
* Production Infrastructure

## 🗺 Roadmap

* ✅ Async FastAPI
* ✅ PostgreSQL Integration
* ✅ SQLAlchemy Async ORM
* ✅ JWT Authentication
* ✅ Redis Integration
* ✅ Redis Session Management
* ✅ JWT Session Revocation
* ✅ AI Gateway
* ✅ AI Services
* ✅ Structured Logging
* ✅ Rate Limiting
* ✅ Celery Background Workers
* ✅ Nginx Reverse Proxy
* ⏳ Docker
* ⏳ CI/CD
* ⏳ Kubernetes
* ⏳ WebSockets
* ⏳ OpenTelemetry

## 📜 License

This project is licensed under the MIT License.

See the LICENSE file for more information.
