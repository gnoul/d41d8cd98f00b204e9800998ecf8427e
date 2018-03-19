from os import environ as env
CELERY_BROKER_URL = 'amqp://admin:mypass@rabbit:5672//'
CELERY_RESULT_BACKEND = 'redis://redis:kee5shi6Oh@redis:6379/0'
SECRET_KEY = 'top-secret!'

POSTGRES_USER = env.get('POSTGRES_USER', 'pguser1')
POSTGRES_DB = env.get('POSTGRES_DB', 'pddb1')
POSTGRES_PASSWORD = env.get('POSTGRES_PASSWORD', 'ohd7ua2Quu')
POSTGRES_HOST = env.get('POSTGRES_HOST', 'db')
POSTGRES_PORT = env.get('POSTGRES_PORT', 5432)
SQLALCHEMY_DATABASE_URI = f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@' \
                          f'{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
SQLALCHEMY_MIGRATE_REPO = './migrations'
SQLALCHEMY_TRACK_MODIFICATIONS = False
