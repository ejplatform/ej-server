#
# Build static assets
#
FROM ejplatform/tools:latest as assets

COPY ./tasks.py /app/tasks.py

# Compile translations
COPY ./etc/scripts/compilemessages.py /usr/bin/compilemessages
COPY ./locale/ /app/locale/
RUN chmod +x /usr/bin/compilemessages
RUN compilemessages

# Build Sass
WORKDIR /app
ARG THEME=default
COPY ./lib/scss /app/lib/scss
COPY ./lib/themes /app/lib/themes
RUN mkdir -p /app/lib/assets/css/
RUN inv sass --no-watch --theme=${THEME}

# Build javascript assets (TODO)
RUN inv js


#
# Create python packages
#
FROM ejplatform/python:buster as py-modules

# Create django-boogie package
WORKDIR /app
ADD https://github.com/fabiommendes/django-boogie/archive/master.zip /app/boogie.zip
RUN unzip boogie.zip \
 && cd django-boogie-master \
 && python setup.py sdist \
 && cd dist \
 && mv django-boogie* /app/boogie.tar.gz \
 && ls /app \
 && echo "INSTALLED DJANGO-BOOGIE"

# Create hyperpython package
WORKDIR /app
ADD https://github.com/fabiommendes/hyperpython/archive/master.zip /app/hyperpython.zip
RUN unzip hyperpython.zip \
 && cd hyperpython-master \
 && python setup.py sdist \
 && cd dist \
 && mv hyperpython* /app/hyperpython.tar.gz \
 && echo "INSTALLED HYPERPYTHON"


#
# Final image
#
FROM ejplatform/python:deploy

# Set theme and environment variables
ENV DJANGO_SETTINGS_MODULE=ej.settings
ENV DJANGO_ENVIRONMENT=production
ENV PYTHONPATH="/app/src/:$PYTHONPATH"
WORKDIR /app

# Copy requirements and update packages
# Most of the time, this will not install anything new.
COPY ./etc/requirements/ /etc/requirements/
RUN pip install -r /etc/requirements/production.txt

# Copy files
COPY ./.coveragerc /app/.coveragerc
COPY ./docker/nginx.conf /etc/nginx/conf.d/web.conf
COPY ./lib/ /app/lib/
COPY ./locale/ /app/locale/
COPY ./manage.py /app/manage.py
COPY ./src/ /app/src/

# Copy django boogie
COPY --from=py-modules /app/*.tar.gz /app/
RUN pip install /app/*.tar.gz \
 && rm /app/*.tar.gz

# Set enviroment variables
ARG COUNTRY=usa
ARG HOSTNAME=localhost
ARG THEME=default
ENV COUNTRY=${HOSTNAME}
ENV EJ_THEME=${THEME}
ENV HOSTNAME=${HOSTNAME}

# Prepare deploy assets
COPY ./tasks.py /app/tasks.py
RUN mkdir -p local/logs local/static/ local/media/ local/db/ \
 && python manage.py collectstatic --noinput \
 && echo "COLLECTED STATIC ASSETS"

 # Copy build-time assets: CSS, JS, i18n
COPY --from=assets /app/lib/assets/css/ /app/lib/assets/css/
COPY --from=assets /app/locale/ /app/locale/

# Create django user
RUN groupadd -r django \
 && useradd -r -g django django \
 && chown -R django:django /app
USER django

# Save commit info
ARG COMMIT_TITLE=none
ARG COMMIT_HASH=none
RUN echo "${COMMIT_HASH}: ${COMMIT_TITLE}" > commit.txt


# Entry point defaults to inv run
EXPOSE 5000
ENTRYPOINT ["inv"]
CMD ["bash"]
