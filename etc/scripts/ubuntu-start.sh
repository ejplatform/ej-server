#!/bin/sh

echo Initialize a new Ubuntu 18.04 VM
echo Please execute as "sh ubuntustart.sh <ip address>"
echo Connecting to $1 ...

ssh root@$1 <<-'ENDSSH'
    apt update
    apt install git docker-compose
    snap install docker
    git clone http://github.com/ejplatform/ej-server
ENDSSH
