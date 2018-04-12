#!/bin/sh

# wait for RabbitMQ server to start
sleep 10

# run Celery worker for our project with Celery configurations
cd /app
celery worker -A ej.math -l info
