import os
from speech_recording import settings
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "speech_recording.settings")
app = Celery()

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.task_default_queue = settings.env("CELERY_QUEUE_NAME")
app.autodiscover_tasks()
