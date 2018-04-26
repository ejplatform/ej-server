# Local Docker

The image defined in this directory is used as the development environment, including for testing (manually and inside of CI/CD pipeline).

## Build Locally

```bash
sudo docker-compose -f docker/local/build.yml build
```

## Perform Tests with Compose

```bash
sudo docker-compose -f docker/local/test.yml run -p ejtest --rm django
sudo docker-compose -f docker/local/test.yml run -p ejtest down
```

## Start with Compose

```bash
sudo docker-compose -f docker/local/start.yml -p ej up -d
```

## Only Set Environment

```bash
sudo docker-compose -f docker/local/idle.yml -p ej up -d
```

* The services `django`, `flower` and `worker` will start as idle.

### Start Manually

```bash
sudo docker-compose -f docker/local/idle.yml -p ej exec django /runserver.sh
sudo docker-compose -f docker/local/idle.yml -p ej exec flower /start_flower.sh
sudo docker-compose -f docker/local/idle.yml -p ej exec worker /start_celery.sh
```

### Test Manually

```bash
sudo docker-compose -f docker/local/idle.yml -p ej exec django /test.sh
```

or

```bash
sudo docker-compose -f docker/local/start.yml -p ej exec django /test.sh
```
