FROM ejplatform/ej-server:base

RUN groupadd -r django \
    && useradd -r -g django django \
    && chown django:django /*.sh

RUN pip install -r /app/requirements/production.txt \
    && pip install invoke

COPY . /app

RUN export $(cat /app/env.example | grep -v ^# | xargs) \
    && python /app/manage.py collectstatic --noinput \
    && mkdir /app/local \
    && echo $BUILD >> /app/local/build.info \
    && cd /app \
    && chown -R django:django /app

WORKDIR /app

USER django

CMD ["/gunicorn.sh"]
