#!/bin/sh

echo Initialize a new Ubuntu 18.04 VM
echo Please execute as "sh ubuntu-start.sh <ip address>"
echo Connecting to $1 ...

ssh root@$1 <<-'ENDSSH'
    apt update
    apt install git docker-compose python3-pip --yes
    snap install docker
    snap install micro --classic
    pip3 install invoke toml
    git clone http://github.com/ejplatform/ej-server
ENDSSH
