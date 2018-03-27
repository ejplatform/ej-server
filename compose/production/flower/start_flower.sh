#! /bin/bash

sleep 10

cd /app
celery flower -A ej.math --address=0.0.0.0 --port=8001
