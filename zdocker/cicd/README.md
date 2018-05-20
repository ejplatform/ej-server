# `ejplatform/ej-cicd:latest` Docker

This image is used as the default CI/CD image.

## Pull from [Docker Hub](https://hub.docker.com/r/ejplatform/ej-cicd/)

```bash
sudo docker pull ejplatform/ej-cicd:latest
```

## Build Locally

```bash
sudo docker-compose -f docker/cicd/build.yml build
```

## Push Changes to [Docker Hub](https://hub.docker.com/r/ejplatform/ej-cicd/)

* If you have permission to push to [ejplatform repository](https://hub.docker.com/r/ejplatform):

```bash
sudo docker login
sudo docker-compose -f docker/cicd/build.yml build
sudo docker-compose -f docker/cicd/build.yml push
```

* Remember to notify the team about the new version of the CI/CD image since the CI will start to use the new version.
