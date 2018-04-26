# `ejplatform/ej-server:base` Docker

This image is used as the default image for all others `ej-server` images, such as: `ej-server:local`, `ej-server:develop`, and `ej-server:latest`.

## Pull from [Docker Hub](https://hub.docker.com/r/ejplatform/ej-server/)

```bash
sudo docker pull ejplatform/ej-server:base
```

## Build Locally

```bash
sudo docker-compose -f docker/base/build.yml build
```

## Push Changes to [Docker Hub](https://hub.docker.com/r/ejplatform/ej-server/)

* If you have permission to push to [ejplatform repository](https://hub.docker.com/r/ejplatform):

```bash
sudo docker login
sudo docker-compose -f docker/base/build.yml build
sudo docker-compose -f docker/base/build.yml push
```

* Remember to notify the team about the new version of the base image since everyone must re-build their local dockers and the CI will start to use the new version.
