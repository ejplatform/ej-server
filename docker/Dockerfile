#===============================================================================
# BASE PYTHON IMAGE
# Install basic packages from APT and PIP
#===============================================================================

FROM debian:buster-slim as python

# Set environment variables
ENV LANG=C.UTF-8
ENV DJANGO_SETTINGS_MODULE=ej.settings
ENV DJANGO_ENVIRONMENT=production
ENV PYTHONPATH="/app/src/:$PYTHONPATH"
ENV PATH=/app/lib/node_modules/.bin/:$PATH
WORKDIR /app

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
 && pip3 install sidekick \
 && ln -s /usr/bin/python3 /usr/bin/python \
 && ln -s /usr/bin/pip3 /usr/bin/pip \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /root/.cache/* \
 && echo "EXTRA PACKAGE INSTALLATION IS DONE!"

# Install core Python deps
COPY ./etc/requirements.txt /app/etc/
RUN pip3 install -r etc/requirements.txt \
 && echo "FINISH INSTALLING PYTHON BASE DEPENDENCIES"

# Create django user
RUN groupadd -r django -g 1000 \
 && useradd -r -g django django -u 1000 \
 && mkdir /home/django \
 && mkdir /app/lib/ \
 && chown -R django:django /app \
 && chown django:django /home/django \
 && chown django:django /app/lib \
 && echo "DJANGO USER CREATED"

# Entry point defaults to inv run
EXPOSE 8000
ENTRYPOINT ["inv"]
CMD ["bash"]


#===============================================================================
# BASE TOOLS IMAGE
#===============================================================================

FROM python as tools

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
        pnpm \
        parcel \
 && echo "NPM PACKAGES INSTALLATION IS DONE!"

# Install core Python deps
COPY ./etc/requirements-dev.txt  /app/etc/
RUN pip3 install -r etc/requirements-dev.txt \
 && echo "FINISH INSTALLING PYTHON DEV DEPENDENCIES"

# Install core JS deps
USER django
COPY ./lib/package.json ./lib/pnpm-lock.yaml /app/lib/
RUN cd lib && pnpm install \
 && echo "INSTALLED JS DEPENDENCIES"


#===============================================================================
# BASE BUILDER IMAGE
#===============================================================================

FROM tools as builder

COPY ./.coveragerc ./*.py ./*.rst ./*.toml /app/
COPY ./etc/ /app/etc/
COPY ./docs/ /app/docs/
COPY ./locale/ /app/locale/
COPY ./lib/ /app/lib/
COPY ./src/ /app/src/

# Prepare assets
RUN mkdir -p local/logs local/static/ local/media/ local/db/ lib/build/
RUN inv -e i18n -c -l pt_BR
RUN inv -e i18n -c -l en_US
RUN inv -e build-assets
RUN echo "BUILT AND COLLECTED STATIC ASSETS"


#===============================================================================
# BASE DEPLOYMENT IMAGE
#===============================================================================

FROM python as deploy


# Set basic parameters
ARG THEME=default
ENV EJ_THEME=${THEME}
USER django

# Copy build assets and source code
COPY --from=builder --chown=django:django /app/locale /app/locale/
COPY --from=builder --chown=django:django /app/lib/build/ /app/lib/build/
COPY --chown=django:django ./lib/assets/ /app/lib/assets/
COPY --chown=django:django ./src/ /app/src/
COPY --chown=django:django *.py *.toml /app/

# Save commit info
ARG COMMIT_TITLE=none
ARG COMMIT_HASH=none
RUN echo "${COMMIT_HASH}: ${COMMIT_TITLE}" > commit.txt

# Collect static files
RUN inv -e collect

# Default command
CMD ["collect", "db", "-m", "gunicorn"]


#===============================================================================
# BASE DEVELOPMENT IMAGE
#===============================================================================

FROM tools as local


# Set environment variables from docker arguments
ARG UID=1000
ARG GID=1000
ARG USERNAME=user

# Configure environment
ENV DJANGO_ENVIRONMENT=local
ENV DJANGO_DEBUG=true
ENV PYTHONUNBUFFERED=1
ENV PATH=$PATH:/opt/node_modules/.bin/

# Make node_modules executables available even after mounting over /app
RUN mv /app/lib/node_modules /opt/node_modules/

# Create user
# Create django user
RUN if [$UID != 1000] \
then \
    groupadd -r ${USERNAME} -g ${GID} \
    useradd -r -g ${USERNAME} ${USERNAME} -u ${UID} \
    mkdir /home/${USERNAME} \
    chown ${USERNAME}:${USERNAME} /home/django \
    echo "USER CREATED" \
fi;
USER ${USERNAME}


COPY ./tasks.py /app/
