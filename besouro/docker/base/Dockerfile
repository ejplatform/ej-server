FROM debian:buster-slim

ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    PYTHONPATH="/app/src/:$PYTHONPATH"

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      bundler \
      curl \
      gcc \
      gettext \
      git \
      gnupg2 \
      libc6-dev \
      libdpkg-perl \
      make \
      nodejs=8.11.2~dfsg-1 \
      python3.6 \
      python3.6-dev \
      python3-pip \
      python3-setuptools \
      ruby-full=1:2.5.1 \
      ruby-sass && \
    pip3 install --upgrade pip

RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg \
      | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" \
      | tee /etc/apt/sources.list.d/yarn.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
      yarn && \
    apt-get clean
