FROM ejplatform/local:latest

# Configure environment
ENV DJANGO_SETTINGS_MODULE=ej.settings
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/src/:$PYTHONPATH"
WORKDIR /app

# Copy necessary files
COPY ./requirements.txt /app/requirements.txt
COPY ./etc/scripts/ /app/etc/scripts/
COPY ./tasks.py /app/tasks.py

# Install dependencies
RUN pip install -r requirements.txt

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
