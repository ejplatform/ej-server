FROM ejplatform/local:latest

# Configure environment
ENV DJANGO_SETTINGS_MODULE=ej.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/src/:$PYTHONPATH"
WORKDIR /app

# Copy necessary files
COPY ./etc/ /app/etc/
COPY ./tasks.py /app/tasks.py

# Install dependencies
RUN pip install -r etc/requirements.txt -r etc/requirements-dev.txt

ARG UID=1000
ARG GID=1000

# Create django user
RUN groupadd -r django -g ${GID} \
 && useradd -r -g django django -u ${UID} \
 && chown -R django:django /app \
 && chown -R django:django /vendor \
 && echo "DJANGO USER CREATED"

# Entry point defaults to inv run
EXPOSE 8000
ENTRYPOINT ["inv"]
CMD ["bash"]
