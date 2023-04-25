FROM python:3.7.10 as base
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
RUN touch /etc/apt/preferences.d/nodejs && \
    echo "Package: nodejs\nPin: origin deb.nodesource.com\nPin-Priority: 1001" > /etc/apt/preferences.d/nodejs
RUN curl -sL https://deb.nodesource.com/setup_12.x | bash - \
    && apt install nodejs -y && npm install -g yarn webpack@4.6.0
RUN curl -sSL https://install.python-poetry.org | python3 -
COPY ./ /ej-application
WORKDIR ej-application

# Installs only production dependencies
FROM base as baseprod
RUN /root/.local/bin/poetry install --without dev

# Installs all dependencies.
FROM baseprod as basedev
RUN /root/.local/bin/poetry install --only dev
