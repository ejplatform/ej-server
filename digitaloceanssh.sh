sshpass  ssh -o StrictHostKeyChecking=no $1@$2 <<-'ENDSSH'   
    cd /app/docker/
    docker-compose -f docker-compose.deploy.yml down
    docker rmi $(docker images -q) -f
    docker network prune -f
    docker-compose -f docker-compose.deploy.yml up -d
    docker-compose -f docker-compose.rocket.yml up -d
ENDSSH
