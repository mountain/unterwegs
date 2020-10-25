from celery import Celery

app = Celery('tasks', broker='redis://redis')
