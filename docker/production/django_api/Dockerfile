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


ADD . /app
WORKDIR /app
RUN pip install -r etc/requirements/production.txt

ARG VOLATILE_DEPENDENCIES_STRATEGY=unknown
RUN VOLATILE_DEPENDENCIES_STRATEGY=${VOLATILE_DEPENDENCIES_STRATEGY} pip install -r etc/requirements/git-modules.txt

COPY etc/scripts/**/* /

RUN groupadd -r django \
    && useradd -r -g django django \
    && chown django:django /*.sh

RUN chown -R django:django /app && ln -s /usr/bin/python3 /usr/bin/python

USER django

CMD ["inv", "run", "--gunicorn", "--migrate"]
