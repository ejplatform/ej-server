FROM ejplatform/local:latest

# Configure environment
ENV DJANGO_SETTINGS_MODULE=ej.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/src/:$PYTHONPATH"
WORKDIR /app

# Copy necessary files
COPY ./etc/requirements/ /app/etc/requirements/
COPY ./etc/scripts/ /app/etc/scripts/
COPY ./tasks.py /app/tasks.py

# Install dependencies
RUN inv update-deps --all --vendor /vendor

# Move vendorized apps away from /app
RUN mv /app/local/vendor/ /vendor/ \
 && echo "RELOCATED PYTHON MODULES"

ARG UID=1000
ARG GID=1000

# Create django user
RUN groupadd -r django -g ${GID} \
 && useradd -r -g django django -u ${UID} \
 && chown -R django:django /app \
 && chown -R django:django /vendor \
 && echo "DJANGO USER CREATED"

# Copy crontab file to cron directory
RUN cp /app/etc/scripts/crontab /etc/cron.d/backup_cron
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/backup_cron
# Apply cron job
# Still needing to run the cron, will be done on inv run
RUN crontab /etc/cron.d/backup_cron

# Entry point defaults to inv run
EXPOSE 8000
ENTRYPOINT ["inv"]
CMD ["bash"]
