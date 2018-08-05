#!/usr/bin/env bash

# Variables and versions
DOCKER_INVOKE=ejplatform/docker-invoke:$1
PYTHON=ejplatform/python:$1
BUILDER=ejplatform/builder:$1


# Build docker-invoke
cd docker/images/docker-invoke/
echo "BUILDING $DOCKER_INVOKE"
docker build . -t $DOCKER_INVOKE --cache-from $DOCKER_INVOKE
docker push $DOCKER_INVOKE
cd ../../..


# Build python
cd docker/images/python/
echo "BUILDING $PYTHON"
docker build . -t $PYTHON --cache-from $PYTHON
docker push $PYTHON
cd ../../..


# Build builder
cd docker/images/builder/
echo "BUILDING $BUILDER"
docker build . -t $BUILDER --cache-from $BUILDER
docker push $BUILDER
cd ../../..


