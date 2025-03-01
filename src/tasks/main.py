from celery import Celery
from src.core.config import AppConfig

celery_app = Celery(
    "tasks",
    broker=AppConfig.BROKER_URL,
    backend=AppConfig.BROKER_URL,
    broker_connection_retry_on_startup=True,
)

# define other configuration such as queue here
celery_app.autodiscover_tasks(["src.tasks"], force=True)
