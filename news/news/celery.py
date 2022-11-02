import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news.settings')

app = Celery('news')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'action_every_monday_8am': {
        'task': 'simpleapp.tasks.send_subscribe',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
    },
}

# celery -A news worker -l INFO -B