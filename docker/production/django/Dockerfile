FROM debian:buster-slim

ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    PYTHONPATH="/app/src/:$PYTHONPATH"

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

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install -y yarn --no-install-recommends \
    && apt-get clean

# ej-server Dependencies
WORKDIR /dependencies

COPY ./etc/npm_globals.txt /dependencies/npm_globals.txt
RUN < npm_globals.txt xargs yarn global add

COPY ./etc/requirements/*.txt /dependencies/
RUN pip install -r /dependencies/production.txt

ARG VOLATILE_DEPENDENCIES_STRATEGY=unknown
RUN VOLATILE_DEPENDENCIES_STRATEGY=${VOLATILE_DEPENDENCIES_STRATEGY} pip install -r /dependencies/git-modules.txt

COPY ./etc/scripts/**/* /

RUN groupadd -r django \
    && useradd -r -g django django \
    && chown django:django /*.sh

WORKDIR /app
COPY . /app

RUN inv prepare-deploy \
    && chown -R django:django /app \
    && ln -s /usr/bin/python3 /usr/bin/python

USER django

CMD ["inv", "run", "--gunicorn", "--migrate", "--assets"]
