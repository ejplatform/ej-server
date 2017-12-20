#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

# run Celery worker for our project myproject with Celery configuration stored in Celeryconf
cd /app
celery worker -A pushtogether.math.celeryconf -Q default -n default@%h -l info 
