FROM debian:buster-slim

# Set environment variables
ENV PYTHONUNBUFFERED = 1
ENV LANG = C.UTF-8
ENV PYTHONPATH = "/app/src/:$PYTHONPATH"


# Install stable Debian dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        bundler \
        curl \
        git \
        gnupg2 \
        gettext \
        nodejs=8.11.2~dfsg-1 \
        python3.6 \
        python3-pip \
        python3-setuptools \
        ruby-sass \
 && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
 && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
 && apt-get update && apt-get install -y --no-install-recommends yarn \
 && rm -rf /var/lib/apt/lists/* \
 && pip3 install --upgrade pip setuptools invoke ~= 0.23


# Install stable EJ dependencies
COPY ./etc/requirements/ /etc/requirements/
RUN < /etc/requirements/npm_globals.txt xargs yarn global add \
 && pip install -r /etc/requirements/base.txt
RUN pip install -r /etc/requirements/production.txt


# Clone volatile dependencies and install them
COPY ./etc/scripts/install-deps.py /app/etc/scripts/install-deps.py
RUN python3 /app/etc/scripts/install-deps.py


# Copy files
EXPOSE 5000
WORKDIR /app
COPY . /app

# Create django user
RUN groupadd -r django \
 && useradd -r -g django django \
 && chown django:django /app/etc/scripts/ -r


ARG THEME=default
ENV THEME=${THEME}

ARG VOLATILE_DEPENDENCIES_STRATEGY=unknown
RUN VOLATILE_DEPENDENCIES_STRATEGY=${VOLATILE_DEPENDENCIES_STRATEGY} pip install -r /dependencies/git-modules.txt

RUN inv prepare-deploy \
    && chown -R django:django /app \
    && ln -s /usr/bin/python3 /usr/bin/python

USER django

CMD ["inv", "run", "--gunicorn", "--assets"]
