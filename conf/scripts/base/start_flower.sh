#! /bin/bash

sleep 10

printf "\n## Starting Flower\n\n"
cd /app
celery flower -A ej.math --address=0.0.0.0 --port=8001
