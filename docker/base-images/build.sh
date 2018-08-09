#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

# Build python alpine
echo "BUILD PYTHON ALPINE IMAGE"
docker build . -f Dockerfile-python_alpine -t ejplatform/python:alpine

# Build python buster
echo; echo; echo "BUILD PYTHON ALPINE IMAGE"
docker build . -f Dockerfile-python_buster -t ejplatform/python:buster

# Build tools
echo "BUILD TOOLS IMAGE"
docker build . -f Dockerfile-tools -t ejplatform/tools:latest

# Build python images
cp ../../etc/requirements/local.txt requirements-local.txt
cp ../../etc/requirements/develop.txt requirements-develop.txt
cp ../../etc/requirements/production.txt requirements-production.txt

echo; echo; echo "BUILD PYTHON IMAGES"
docker build . -f Dockerfile-python_deploy -t ejplatform/python:deploy
docker build . -f Dockerfile-python_test -t ejplatform/python:test
docker build . -f Dockerfile-local -t ejplatform/local:latest

# Check if user wants to publish
if [ $# -eq 1 ]; then
    if [ "$1" = "publish" ]; then
        echo; echo; echo "PUBLISHING IMAGES"
        docker push ejplatform/python:alpine;
        docker push ejplatform/python:buster;
        docker push ejplatform/tools:latest;
        docker push ejplatform/python:deploy;
        docker push ejplatform/python:test;
        docker push ejplatform/local:latest;
    fi
else
    echo "Execute 'sh build.sh publish' to publish images"
fi

# Clean requirements
rm requirements*.txt
