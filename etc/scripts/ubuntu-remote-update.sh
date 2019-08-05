#!/bin/sh

echo "This script assumes that EJ source code is under /root/ej-server and the"
echo "Docker-Compose configuration was setup under <repo>/deploy/"
echo "In the future, we will probably move to Ansible."
echo ""
echo 'Please execute as "sh ubuntu-remote-update.sh <ip address> <theme> <org> <tag>"'
echo "Connecting to $1 ..."

ssh root@$1 <<-'ENDSSH'
    # Set env
    export IP_ADDR=$1
    export EJ_THEME=$2
    export ORG=$3
    export TAG=$4

    # Start
    echo "Building $org/*:$tag for $1 using $2 theme"

    # Update repository
    cd ej-server
    git pull

    # Go to folder and build images
    cd deploy
    docker-compose build --build-arg TAG=$TAG --build-arg THEME=$EJ_THEME --build-arg ORG=$ORG
    docker-compose down
    docker-compose up -d
ENDSSH

