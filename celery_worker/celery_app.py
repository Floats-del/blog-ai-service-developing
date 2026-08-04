from celery import Celery

celery_app = Celery(
    "fastapi_ai_backend",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

celery_app.conf.imports = (
    "celery_worker.tasks.demo_tasks",
    "celery_worker.tasks.Ai_worker"
)
