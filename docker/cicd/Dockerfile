FROM docker

RUN apk add --no-cache git py-pip \
    && pip install --upgrade pip \
    && pip install docker-compose \
    && pip install rancher-gitlab-deploy \
    && ln -s /usr/bin/rancher-gitlab-deploy /usr/bin/upgrade
