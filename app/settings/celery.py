import os

from celery import Celery
from celery.signals import after_setup_logger, setup_logging

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

app = Celery("proj")
app.config_from_object("django.conf:settings", namespace="CELERY")


@setup_logging.connect
def config_loggers(*args, **kwargs):
    from logging.config import dictConfig

    from django.conf import settings

    dictConfig(settings.LOGGING)


app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
    return True
