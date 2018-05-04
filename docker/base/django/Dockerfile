FROM debian:buster-slim

ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8

RUN apt-get update && apt-get install -y \
    bundler \
    curl \
    gcc \
    git \
    gnupg2 \
    libc6-dev \
    libdpkg-perl \
    make \
    nodejs=8.11.1~dfsg-2 \
    python3=3.6.4-1 \
    python3-dev=3.6.4-1 \
    python3-pip \
    python3-setuptools \
    ruby-full=1:2.5.1 \
    --no-install-recommends \
    && pip3 install --upgrade pip

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y yarn --no-install-recommends \
    && apt-get clean

# ej-server Dependencies
WORKDIR /dependencies

COPY ./Gemfile /dependencies/Gemfile
RUN bundler install --verbose

COPY ./npm_globals.txt /dependencies/npm_globals.txt
RUN < npm_globals.txt xargs yarn global add

COPY ./requirements/base.txt /dependencies/base.txt
RUN pip install -r base.txt

# Scripts
COPY ./docker/base/script /

ENTRYPOINT ["/entrypoint.sh"]
