FROM debian:buster-slim

ARG API_TAG

EXPOSE 5000

# Install debian dependencies
RUN apt-get update \
    && apt-get install -y \
    bundler \
    curl \
    gcc \
    git \
    gnupg2 \
    libc6-dev \
    libdpkg-perl \
    ruby-sass \
    make \
    nodejs=8.11.2~dfsg-1 \
    python3.6 \
    python3.6-dev \
    python3-pip \
    python3-setuptools \
    ruby-full=1:2.5.1 \
    gettext \
    --no-install-recommends \
    && pip3 install --upgrade pip


RUN git clone --single-branch -b "${API_TAG}" \
https://github.com/unidoscontraacorrupcao/ej-server.git #rebuild

WORKDIR ej-server

ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8

RUN pip install -r etc/requirements/production.txt
RUN pip install invoke
ARG VOLATILE_DEPENDENCIES_STRATEGY=unknown
RUN VOLATILE_DEPENDENCIES_STRATEGY=${VOLATILE_DEPENDENCIES_STRATEGY} pip install -r etc/requirements/git-modules.txt

RUN groupadd -r django && useradd -r -g django django
RUN chown -R django:django . && ln -s /usr/bin/python3 /usr/bin/python
USER django
ENTRYPOINT ./manage.py migrate
