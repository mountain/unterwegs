from flask_appfactory.celery import celeryfactory
from .app import create_app

celery = celeryfactory(create_app())
