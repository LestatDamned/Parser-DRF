import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ParserdjangoProject.settings')
app = Celery('ParserdjangoProject', broker_connection_retry=False,
             broker_connection_retry_on_startup=True, )
app.config_from_object('django.conf:settings', namespace='CELERY')
broker_connection_retry = False
app.conf.update(result_extended=True)

app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')