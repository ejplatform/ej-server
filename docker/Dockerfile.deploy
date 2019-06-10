#
# Build static assets
#
FROM ejplatform/tools:latest as assets


# Compile translations
COPY ./etc/scripts/compilemessages.py /usr/bin/compilemessages
COPY ./locale/ /app/locale/
WORKDIR /app
RUN chmod +x /usr/bin/compilemessages \
 && compilemessages


# Build Sass
ARG THEME=default
COPY ./lib/scss /app/lib/scss
COPY ./lib/themes /app/lib/themes
COPY ./tasks.py /app/tasks.py
RUN mkdir -p /app/lib/build/css/ \
 && inv -e sass --theme=${THEME}

# Build javascript assets (TODO)
RUN inv -e js

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
COPY ./lib/ /app/lib/
COPY ./locale/ /app/locale/
COPY ./manage.py /app/manage.py
COPY ./src/ /app/src/
COPY ./docs/ /app/docs

RUN sphinx-build docs/ /app/build/docs

# Set environment variables
ARG COUNTRY=brasil
ARG HOSTNAME=localhost
ARG THEME=default
ENV COUNTRY=${COUNTRY}
ENV EJ_THEME=${THEME}
ENV HOSTNAME=${HOSTNAME}

# Copy build-time assets: CSS, JS, i18n
COPY --from=assets /app/lib/build/ /app/lib/build/
COPY --from=assets /app/locale/ /app/locale/

# Prepare deploy assets
COPY ./tasks.py /app/tasks.py
RUN mkdir -p local/logs local/static/ local/media/ local/db/ \
 && python manage.py collectstatic --noinput \
 && echo "COLLECTED STATIC ASSETS"

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
EXPOSE 8000
ENTRYPOINT ["inv"]
CMD ["bash"]
