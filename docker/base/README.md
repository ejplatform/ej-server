# Base Docker Images

These images are used as the default images for others `ej-server` images, such as: `ej-server:local`, `ej-server:develop`, and `ej-server:latest`.

* `ej-server:base` contains the base requirements from the Django project;
* `ej-server:base-test` inherits the base requirements from `ej-server:base` and also contains the test requirements from the Django project;
* `ej-server:base-production` inherits the base requirements from `ej-server:base` and also contains the production requirements from the Django project.

## Pull from [Docker Hub](https://hub.docker.com/r/ejplatform/ej-server/)

* Base image:

    ```bash
    sudo docker pull ejplatform/ej-server:base
    ```
* Test base image:

    ```bash
    sudo docker pull ejplatform/ej-server:base-test
    ```
* Production base image:

    ```bash
    sudo docker pull ejplatform/ej-server:base-production
    ```

## Build Locally

* Base image:

    ```bash
    sudo docker-compose -f docker/base/base.build.yml build
    ```
* Test base image:

    ```bash
    sudo docker-compose -f docker/base/test.build.yml build
    ```
* Production base image:

    ```bash
    sudo docker-compose -f docker/base/production.build.yml build
    ```

## Push Changes to [Docker Hub](https://hub.docker.com/r/ejplatform/ej-server/)

### Changes in Base image

* Every change to `ej-server:base` also changes `ej-server:base-test` and `ej-server:base-production`. All three must be pushed at once in this case;
* If you have permission to push to [ejplatform repository](https://hub.docker.com/r/ejplatform):

    ```bash
    sudo docker login

    sudo docker-compose -f docker/base/base.build.yml build
    sudo docker-compose -f docker/base/test.build.yml build
    sudo docker-compose -f docker/base/production.build.yml build

    sudo docker-compose -f docker/base/base.build.yml push
    sudo docker-compose -f docker/base/test.build.yml push
    sudo docker-compose -f docker/base/production.build.yml push
    ```
* Remember to notify the team about the new version of the base image since everyone must re-build their local dockers and the CI will start to use the new version.

### Changes in Test Base image

* If you have permission to push to [ejplatform repository](https://hub.docker.com/r/ejplatform):

    ```bash
    sudo docker login

    sudo docker-compose -f docker/base/test.build.yml build
    sudo docker-compose -f docker/base/test.build.yml push
    ```
* Remember to notify the team about the new version of the base image since everyone must re-build their local dockers and the CI will start to use the new version.

### Changes in Production Base image

* If you have permission to push to [ejplatform repository](https://hub.docker.com/r/ejplatform):

    ```bash
    sudo docker login

    sudo docker-compose -f docker/base/production.build.yml build
    sudo docker-compose -f docker/base/production.build.yml push
    ```
