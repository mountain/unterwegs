MAX_CONTENT_LENGTH = 1024 * 1024 * 40

UPLOAD_EXTENSIONS = '*.pdf'

EXTENSIONS = [
    'flask_celeryext:FlaskCeleryExt',
]

BROKER_URL = "redis://redis:6379/0"

PACKAGES = [
    'unterwegs.tasks.converter',
    'unterwegs.tasks.indexer',
    'unterwegs.tasks.splitter',
    'unterwegs.tasks.uploader',
]
