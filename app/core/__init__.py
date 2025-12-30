from celery import Celery
import os

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "pyamqp://guest@mq//"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "rpc://"),
)

celery_app.conf.update(task_track_started=True)
