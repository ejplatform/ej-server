FROM python:3.7.10
ARG tag
ARG env
# Install debian dependencies
RUN apt-get update \
    && apt-get install -y \
    curl \
    gcc \
    git \
    ruby-sass \
    gnupg2 \
    libc6-dev \
    libdpkg-perl \
    make \
    gettext
# Move ej nginx conf to nginx volume
RUN touch /etc/apt/preferences.d/nodejs && \
    echo "Package: nodejs\nPin: origin deb.nodesource.com\nPin-Priority: 1001" > /etc/apt/preferences.d/nodejs
RUN curl -sL https://deb.nodesource.com/setup_10.x | bash - \
    && apt install nodejs -y && npm install -g yarn webpack@4.6.0
COPY ./ /ej-application
WORKDIR ej-application
RUN pip install poetry
# https://github.com/pypa/setuptools/pull/3207/commits/6e462c7a18c32089bfd4e8c6cb0f3382b7f25c7a
RUN poetry run pip install 'setuptools==61.2.0'
RUN poetry lock --no-update
RUN poetry install
