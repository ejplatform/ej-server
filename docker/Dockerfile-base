FROM debian:buster-slim

# Set environment variables
ENV LANG=C.UTF-8

# Install stable Debian dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.7 \
        python3-pip \
        python3-setuptools \
        python3-venv \
        unzip \
        curl \
        gettext \
        xz-utils \
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /root/.cache/* \
 && echo "BASIC APT INSTALLATION IS DONE!"

# Install pip dependencies
RUN pip3 install --upgrade \
        invoke~=1.0 \
        markupsafe \
        pip \
        poetry \
        psycopg2-binary \
        setuptools \
        toml \
        toolz \
        virtualenvwrapper \
 && pip3 install sidekick \
 && ln -s /usr/bin/python3 /usr/bin/python \
 && ln -s /usr/bin/pip3 /usr/bin/pip \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /root/.cache/* \
 && echo "EXTRA PACKAGE INSTALLATION IS DONE!"

# Install node from binaries (nodejs package in Buster does not contain npm!)
RUN curl https://nodejs.org/dist/v8.11.3/node-v8.11.3-linux-x64.tar.xz -o node.tar.xz \
 && tar -xJf node.tar.xz \
 && mv node-v8.11.3-linux-x64 node \
 && mv /node/bin/* /usr/bin/ \
 && mv /node/lib/node_modules /usr/lib \
 && mv /node/include/node /usr/include \
 && rm -rf node* \
 && echo "NPM INSTALLATION IS DONE!"

# Install global npm packages
RUN npm install -g \
        yarn \
        parcel \
 && echo "NPM PACKAGES INSTALLATION IS DONE!"

# Set theme and environment variables
ENV DJANGO_SETTINGS_MODULE=ej.settings
ENV DJANGO_ENVIRONMENT=production
ENV PYTHONPATH="/app/src/:$PYTHONPATH"
WORKDIR /app

# Install core Python deps
COPY ./etc/requirements-dev.txt /app/etc/requirements-dev.txt
RUN pip3 install -r etc/requirements-dev.txt
COPY ./etc/requirements.txt /app/etc/requirements.txt
RUN pip3 install -r etc/requirements.txt

# Install core JS deps
COPY ./lib/package.json /app/lib/package.json
RUN cd lib && npm install \
 && echo "INSTALLED JS DEPENDENCIES"

# Set environment variables from docker arguments
ARG COUNTRY=brazil
ARG HOSTNAME=localhost
ARG THEME=default
ARG UID=1000
ARG GID=1000
ENV COUNTRY=${COUNTRY}
ENV EJ_THEME=${THEME}
ENV HOSTNAME=${HOSTNAME}

# Create django user
RUN groupadd -r django -g ${GID} \
 && useradd -r -g django django -u ${UID} \
 && chown -R django:django /app \
 && echo "DJANGO USER CREATED"

# Save commit info
ARG COMMIT_TITLE=none
ARG COMMIT_HASH=none
RUN echo "${COMMIT_HASH}: ${COMMIT_TITLE}" > commit.txt

# Entry point defaults to inv run
EXPOSE 8000
ENTRYPOINT ["inv"]
CMD ["bash"]
