FROM python:3.6

ENV PYTHONUNBUFFERED 1


WORKDIR /app

COPY ./requirements /app/requirements
RUN pip install -r /app/requirements/test.txt

COPY ./compose/production/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./compose/dev/django/test.sh /test.sh
RUN sed -i 's/\r//' /test.sh
RUN chmod +x /test.sh

COPY ./compose/local/django/runserver.sh /runserver.sh
RUN sed -i 's/\r//' /runserver.sh
RUN chmod +x /runserver.sh

COPY . /app

ENTRYPOINT ["/entrypoint.sh"]
