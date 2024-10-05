import os
from datetime import timedelta


from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "contentapi.settings")


app = Celery("contentapi")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "pull_content": {
        "task": "pull_and_store_content",
        "schedule": crontab(),
        # "schedule": timedelta(seconds=30),
    },
}
