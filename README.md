<div align="center">

# 🚀 AI-Powered Blog Backend

### A production-oriented FastAPI backend showcasing scalable backend engineering, AI integration, and distributed system concepts.

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge\&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116-009688?style=for-the-badge\&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-316192?style=for-the-badge\&logo=postgresql)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=for-the-badge)](https://www.sqlalchemy.org/)
[![Redis](https://img.shields.io/badge/Redis-7.0-DC382D?style=for-the-badge\&logo=redis)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-Background%20Workers-37814A?style=for-the-badge)](https://docs.celeryq.dev/)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

</div>

---

# 📖 About

This project is my primary backend engineering portfolio project.

Instead of building a simple CRUD application, this backend focuses on production-oriented engineering practices while integrating AI-powered features.

The goal is to design a scalable backend similar to real-world systems using:

* Clean architecture principles
* Async programming
* Service-layer separation
* Distributed background processing
* Structured logging
* Centralized exception handling
* Authentication and authorization systems
* AI service orchestration

---

# ✨ Features

## 🤖 AI Platform

* AI Content Rephrasing
* AI Title Generation
* AI Text Summarization
* AI Sentiment Analysis
* AI Intent Classification
* Structured LLM Outputs
* AI Provider Error Handling
* AI Request Tracking

---

## 🔐 Authentication & Security

* JWT Authentication
* OAuth2 Bearer Authentication
* Password Hashing
* Redis-backed JWT Session Management
* Session Revocation
* Logout From All Devices
* User Ban System
* Protected Routes

---

## ⚡ Backend Engineering

* Async FastAPI
* PostgreSQL Database
* SQLAlchemy Async ORM
* Alembic Migrations
* Pydantic Validation
* Dependency Injection
* Service Layer Architecture
* Centralized Exception Handling
* Standardized API Response Wrapper
* Structured Application Logging

---

## 🚦 Performance & Infrastructure

* Redis Caching
* Redis Session Storage
* SlowAPI Rate Limiting
* Nginx Reverse Proxy
* Celery Background Workers
* Async AI Task Processing
* Task Status Tracking

---

# 🏗 Architecture

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

 Authentication       AI Gateway          API Services
        │                  │                  │
        ▼                  ▼                  ▼

 Redis Sessions     AI Services        Business Logic
 Redis Cache             │                  │
                         ▼                  ▼

                  Celery Workers      PostgreSQL
                         │
                         ▼

                    Redis Broker
                    Redis Results
```

---

# 🧠 AI Request Flow

```text
Client
  |
  v
AI Endpoint
  |
  v
AI Gateway
  |
  ├── Authentication Validation
  |
  ├── Quota Check
  |
  ├── Request Reservation
  |
  v
Celery Task Queue
  |
  v
AI Worker
  |
  v
LLM Processing
  |
  v
Redis Result Backend
  |
  v
Client Polls Task Status
```

---

# 📂 Project Structure

```text
.
├── Ai/
│   ├── title generation
│   ├── summarization
│   ├── sentiment analysis
│   └── intent classification
│
├── celery_worker/
│   ├── celery_app.py
│   └── tasks/
│
├── core/
│   ├── exceptions
│   ├── security
│   └── configuration
│
├── db_tables/
│
├── migrations/
│
├── routers/
│   ├── ai/
│   ├── auth/
│   ├── posts/
│   └── users/
│
├── utils/
│   ├── logging/
│   ├── schemas.py
│   ├── hashing.py
│   └── helpers
│
├── main.py
└── requirements.txt
```

---

# 🛠 Tech Stack

| Category          | Technologies     |
| ----------------- | ---------------- |
| Backend Framework | FastAPI          |
| Language          | Python 3.12      |
| Database          | PostgreSQL       |
| ORM               | SQLAlchemy Async |
| Authentication    | JWT, OAuth2      |
| Validation        | Pydantic         |
| AI Framework      | LangChain        |
| AI Provider       | Groq             |
| AI Monitoring     | LangSmith        |
| Cache             | Redis            |
| Task Queue        | Celery           |
| Rate Limiting     | SlowAPI          |
| Reverse Proxy     | Nginx            |
| Migration Tool    | Alembic          |

---

# 🚀 Getting Started

## Clone repository

```bash
git clone https://github.com/Floats-del/blog-ai-service-developing.git
```

---

## Create virtual environment

```bash
python -m venv .venv
```

---

## Activate environment

Windows:

```bash
.venv\Scripts\activate
```

Linux:

```bash
source .venv/bin/activate
```

---

## Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create `.env`

```env
DATABASE_URL=

HASH_SECRET_KEY=

ALGORITHM=

ACCESS_TOKEN_EXPIRE_MINUTES=

GROQ_API_KEY=

LANGSMITH_API_KEY=
```

---

## Database Migration

```bash
alembic upgrade head
```

---

## Start Application

```bash
uvicorn main:app --reload
```

---

## Start Redis

```bash
redis-server
```

---

## Start Celery Worker

```bash
celery -A celery_worker.celery_app:celery_app worker --loglevel=info
```

---

# 📈 Engineering Focus

Current development focuses on building production-grade backend infrastructure:

* Distributed task processing
* AI workflow orchestration
* Scalable authentication
* Backend observability
* Performance optimization
* Security improvements
* Cloud-ready architecture

---

# 🗺 Roadmap

* ✅ Async FastAPI
* ✅ PostgreSQL Integration
* ✅ SQLAlchemy Async ORM
* ✅ JWT Authentication
* ✅ Redis Integration
* ✅ Redis Session Management
* ✅ JWT Session Revocation
* ✅ AI Services
* ✅ AI Gateway
* ✅ Quota Reservation System
* ✅ Structured Logging
* ✅ Rate Limiting
* ✅ Celery Background Workers
* ⏳ Docker Deployment
* ⏳ CI/CD Pipeline
* ⏳ Kubernetes Deployment
* ⏳ WebSocket Real-Time Updates

---

# 📜 License

This project is licensed under the MIT License.

See the [LICENSE](LICENSE) file for more information.
