#!/usr/bin/env bash

# Build python alpine
echo "BUILD PYTHON ALPINE IMAGE"
sudo docker build . -f Dockerfile-python_alpine -t ejplatform/python:alpine

# Build python buster
echo; echo; echo "BUILD PYTHON ALPINE IMAGE"
sudo docker build . -f Dockerfile-python_buster -t ejplatform/python:buster

# Build tools
echo "BUILD SASS IMAGE"
sudo docker build . -f Dockerfile-sass -t ejplatform/sass:latest

echo "BUILD NODEJS"
sudo docker build . -f Dockerfile-node -t ejplatform/node:latest

# Build python images
cp ../../etc/requirements/base.txt requirements-base.txt
cp ../../etc/requirements/develop.txt requirements-develop.txt
cp ../../etc/requirements/production.txt requirements-production.txt

echo; echo; echo "BUILD PYTHON IMAGES"
sudo docker build . -f Dockerfile-python_install -t ejplatform/python:base --build-arg BASE=buster
sudo docker build . -f Dockerfile-python_install -t ejplatform/python:develop --build-arg INSTALL=develop
sudo docker build . -f Dockerfile-python_install -t ejplatform/python:production --build-arg INSTALL=production

# Check if user wants to publish
if [ $1 == "publish" ]; then
    docker pull ejplatform/python:alpine
    docker pull ejplatform/python:buster
    docker pull ejplatform/python:base
    docker pull ejplatform/python:develop
    docker pull ejplatform/python:production
    docker pull ejplatform/tool:sass
fi
