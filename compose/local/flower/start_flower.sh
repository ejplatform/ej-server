#! /bin/bash

sleep 10

cd /app
celery flower -A pushtogether.math.celeryconf --address=0.0.0.0 --port=8001
