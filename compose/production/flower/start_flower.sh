#! /bin/bash

sleep 10

cd /app
celery flower -A pushtogether.math --address=0.0.0.0 --port=8001
