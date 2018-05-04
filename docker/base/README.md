# Base Docker Images

These images are used as the default images for others `ej-server` images, such as: `ej-server:local`, `ej-server:develop`, and `ej-server:latest`.

* `ej-server:base` contains the ej-server base requirements;
* `ej-server:base-test` inherits the base requirements from `ej-server:base` and also contains the ej-server test requirements;
* `ej-server:base-production` inherits the base requirements from `ej-server:base` and also contains the ej-server production requirements.

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

## Handling Updates with Continuous Integration

Every commit at any branch will run the `test` stage from the `pipeline`.

### Changes in Base Image

Any changes to [requirements/base.txt](https://github.com/ejplatform/ej-server/blob/master/requirements/base.txt), [Gemfile](https://github.com/ejplatform/ej-server/blob/master/Gemfile), or [npm_globals.txt](https://github.com/ejplatform/ej-server/blob/master/npm_globals.txt), must trigger the base build in your branch and the update build in master/develop branches.

To trigger the scripts, use:

```bash
# Only build
git commit -m "{commit description}" -m "build image <base>"
# Build and Update (Only trigger in master/develop branches)
git commit -m "{commit description}" -m "build image <base>" -m "update image <base>"
```

### Changes in Test Base Image

Any changes to [requirements/test.txt](https://github.com/ejplatform/ej-server/blob/master/requirements/test.txt) must trigger the base-test build in your branch and the update build in master/develop branches.

To trigger the scripts, use:

```bash
# Only build
git commit -m "{commit description}" -m "build image <base-test>"
# Build and Update (Only trigger in master/develop branches)
git commit -m "{commit description}" -m "build image <base-test>" -m "update image <base-test>"
```

### Changes in Production Base Image

Any changes to [requirements/production.txt](https://github.com/ejplatform/ej-server/blob/master/requirements/production.txt) must trigger the base-production build in your branch and the update build in master/develop branches.

To trigger the scripts, use:

```bash
# Only build
git commit -m "{commit description}" -m "build image <base-production>"
# Build and Update (Only trigger in master/develop branches)
git commit -m "{commit description}" -m "build image <base-production>" -m "update image <base-test>"
```

## Manually Push Changes to [Docker Hub](https://hub.docker.com/r/ejplatform/ej-server/)

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
