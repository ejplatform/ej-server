FROM ejplatform/base-deps:latest

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/src/:$PYTHONPATH"


# Install stable EJ dependencies
COPY ./etc/requirements/ /etc/requirements/
RUN < /etc/requirements/npm_globals.txt xargs yarn global add \
 && pip install -r /etc/requirements/base.txt \
 && pip install -r /etc/requirements/production.txt \
 && rm -rf ~/.cache/pip/


# Copy files
WORKDIR /app
COPY ./lib/ /app/lib/
COPY ./src/ /app/src/
COPY ./locale/ /app/locale/
COPY ./manage.py /app/manage.py
COPY ./.coveragerc /app/.coveragerc
RUN pip install -r /etc/requirements/git-modules.txt


# Set theme
ARG THEME=default
ENV EJ_THEME=${THEME}
ENV DJANGO_SETTINGS_MODULE=ej.settings
ENV DJANGO_ENVIRONMENT=production
ENV DJANGO_DEBUG=true


# Prepare deploy
COPY ./tasks.py /app/tasks.py
RUN mkdir local/ \
 && mkdir local/logs/ \
 && mkdir local/static/ \
 && mkdir local/media/ \
 && inv prepare-deploy


# Create django user
RUN groupadd -r django \
 && useradd -r -g django django \
 && chown -R django:django /app
USER django


# Entry point defaults to inv run
EXPOSE 5000
ENTRYPOINT ["inv"]
CMD ["bash"]
