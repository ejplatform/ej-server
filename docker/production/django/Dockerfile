FROM ejplatform/ej-server:base-production

RUN groupadd -r django \
    && useradd -r -g django django \
    && chown django:django /*.sh

COPY . /app

RUN export $(cat /app/env.example | grep -v ^# | xargs) \
    && python3 /app/manage.py collectstatic --noinput \
    && mkdir /app/local \
    && echo $BUILD >> /app/local/build.info \
    && cd /app \
    && chown -R django:django /app

WORKDIR /app

USER django

CMD ["/gunicorn.sh"]
