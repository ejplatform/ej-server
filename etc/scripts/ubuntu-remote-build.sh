#!/bin/sh

echo "This script configures a remote Ubuntu 18.04 VM and"
echo "makes it ready for a custom EJ deploy that uses Docker-Compose."
echo "In the future, we will probably move to Ansible."
echo ""
echo 'Please execute as "sh ubuntu-remote-build.sh <ip address> <theme> <org> <tag>"'
echo "Connecting to $1 ..."

ssh root@$1 <<-'ENDSSH'
    # Set env
    export IP_ADDR=$1
    export EJ_THEME=$2
    export ORG=$3
    export TAG=$4

    # Start
    echo "Building $org/*:$tag for $1 using $2 theme"

    # Install deps
    apt update
    apt install git docker-compose python3-pip -y --no-install-recommends
    snap install docker
    snap install micro --classic
    pip3 install invoke toml

    # Clone repository
    git clone http://github.com/ejplatform/ej-server
    cd ej-server
    mkdir -p deploy
    cp docker/* deploy/ -r
    rm deploy/docker-compose* -f
    pwd
    python3 etc/scripts/mergeconfigs.py > deploy/docker-compose.yaml
    ls deploy

    # Go to folder and build images
    cd deploy
    docker-compose build
    micro config.env
    docker-compose run web bash
    docker-compose up
ENDSSH

