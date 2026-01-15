import os
from celery import Celery


broker_url = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@mq:5672//")

celery_app = Celery("app", broker=broker_url, include=["app.tasks"])

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Europe/Moscow",
    enable_utc=True,
)
