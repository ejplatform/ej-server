#!/usr/bin/env bash

# Force exit on errors
set -o errexit
set -o pipefail
set -o nounset

# Variables and versions
WEB=ejplatform/web:$1
DEV=ejplatform/dev:$1
NGINX=ejplatform/nginx:$1

# Build docker images
docker build . -f docker/Dockerfile       -t $WEB   --cache-from $WEB
docker build . -f docker/Dockerfile-dev   -t $DEV   --cache-from $DEV
docker build . -f docker/Dockerfile-nginx -t $NGINX --cache-from $NGINX

# Publish images
docker push $WEB
docker push $DEV
docker push $NGINX
