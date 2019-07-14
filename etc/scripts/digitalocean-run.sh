#!/bin/sh
ssh -o StrictHostKeyChecking=no root@$2 <<-'ENDSSH'
    cd ej-server/docker/
    docker-compose -f docker-compose.deploy.yml down
    docker rmi $(docker images -q) -f
    docker network prune -f
    docker-compose -f docker-compose.deploy.yml up -d
ENDSSH
