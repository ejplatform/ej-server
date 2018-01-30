import os
from kombu import Exchange, Queue

CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = 'America/Sao_Paulo'

# Redis

CELERY_REDIS_PORT = 6379
CELERY_REDIS_DB = 0
CELERY_REDIS_HOST = os.environ.get('REDIS_PORT_6379_TCP_ADDR', 'redis')

RABBIT_HOSTNAME = os.environ.get('RABBIT_PORT_5672_TCP', 'rabbit')

if RABBIT_HOSTNAME.startswith('tcp://'):
    RABBIT_HOSTNAME = RABBIT_HOSTNAME.split('//')[1]

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', None)
if not CELERY_BROKER_URL:
    CELERY_BROKER_URL = 'amqp://{user}:{password}@{hostname}/{vhost}/'.format(
        user=os.environ.get('RABBIT_ENV_USER', 'admin'),
        password=os.environ.get('RABBIT_ENV_RABBITMQ_PASS', 'mypass'),
        hostname=RABBIT_HOSTNAME,
        vhost=os.environ.get('RABBIT_ENV_VHOST', ''))

# We don't want to have dead connections stored on rabbitmq,
# so we have to negotiate using heartbeats
CELERY_BROKER_HEARTBEAT = 30
CELERY_BROKER_POOL_LIMIT = 10
CELERY_BROKER_CONNECTION_TIMEOUT = 10

# Celery configuration

# configure queues, currently we have only one
#CELERY_DEFAULT_QUEUE = 'default'  
#CELERY_QUEUES = (  
#    Queue('default', Exchange('default'), routing_key='default'),
#)

# Sensible settings for celery
CELERY_TASK_ALWAYS_EAGER = False
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_PUBLISH_RETRY = True
CELERY_WORKER_DISABLE_RATE_LIMITS = False

# If you want to see results and try out tasks interactively, change it to False
# Or change this setting on tasks level
#CELERY_TASK_IGNORE_RESULT = False

# Set redis as celery result backend
CELERY_RESULT_BACKEND = 'redis://{host}:{port}/{db}'.format(
    host=CELERY_REDIS_HOST,
    port=CELERY_REDIS_PORT,
    db=CELERY_REDIS_DB)
#CELERY_REDIS_MAX_CONNECTIONS = 20

# Don't use pickle as serializer, json is much safer
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['application/json']

CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000
