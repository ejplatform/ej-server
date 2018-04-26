FROM python:3.6

ENV PYTHONUNBUFFERED 1

COPY ./requirements/base.txt /app/requirements/base.txt

RUN pip install -r /app/requirements/base.txt

COPY ./docker/base/script /

ENTRYPOINT ["/entrypoint.sh"]
