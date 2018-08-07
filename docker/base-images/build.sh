#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

# Build python alpine
echo "BUILD PYTHON ALPINE IMAGE"
sudo docker build . -f Dockerfile-python_alpine -t ejplatform/python:alpine

# Build python buster
echo; echo; echo "BUILD PYTHON ALPINE IMAGE"
sudo docker build . -f Dockerfile-python_buster -t ejplatform/python:buster

# Build tools
echo "BUILD TOOLS IMAGE"
sudo docker build . -f Dockerfile-tools -t ejplatform/tools:latest

# Build python images
cp ../../etc/requirements/local.txt requirements-local.txt
cp ../../etc/requirements/develop.txt requirements-develop.txt
cp ../../etc/requirements/production.txt requirements-production.txt

echo; echo; echo "BUILD PYTHON IMAGES"
sudo docker build . -f Dockerfile-python_install -t ejplatform/python:deploy --build-arg BASE=buster --build-arg INSTALL=production
sudo docker build . -f Dockerfile-python_install -t ejplatform/python:dev --build-arg BASE=deploy --build-arg INSTALL=develop

# Check if user wants to publish
if [ "$1" = "publish" ]; then
    echo; echo; echo "PUBLISHING IMAGES"
    sudo docker push ejplatform/python:alpine;
    sudo docker push ejplatform/python:deploy;
    sudo docker push ejplatform/python:dev;
    sudo docker push ejplatform/python:deploy;
    sudo docker push ejplatform/tools:latest;
else
    echo "Execute 'sh build.sh publish' to publish images"
fi

# Clean requirements
rm requirements*.txt
