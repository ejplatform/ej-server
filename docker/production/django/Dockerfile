FROM debian:buster-slim

ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    PYTHONPATH="/app/src/:$PYTHONPATH"

EXPOSE 5000

# Install fixed Debian dependencies
RUN apt-get update && apt-get install -y \
        bundler \
        curl \
        gcc \
        git \
        gnupg2 \
        libc6-dev \
        libdpkg-perl \
        ruby-sass \
        make \
        python3.6 \
        python3.6-dev \
        python3-pip \
        python3-setuptools \
        ruby-full=1:2.5.1 \
        gettext \
        --no-install-recommends \
 && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
 && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install --upgrade pip \
 && gem install sass

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash - \
    && apt-get install -y nodejs


# ej-server Dependencies
WORKDIR /dependencies

COPY ./etc/npm_globals.txt /dependencies/npm_globals.txt

RUN npm install -g yarn
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

ARG THEME=default
ENV THEME=${THEME}
RUN inv prepare-deploy \
    && chown -R django:django /app

USER django

CMD ["inv", "run", "--gunicorn", "--assets"]
