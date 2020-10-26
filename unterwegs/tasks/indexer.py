from celery import shared_task


@shared_task
def fire(t):
    return t

