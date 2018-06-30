FROM besouro/ej-server:deps

COPY ./etc/scripts/**/* /

RUN groupadd -r django \
    && useradd -r -g django django \
    && chown django:django /*.sh

WORKDIR /app

COPY . /app

RUN inv prepare-deploy \
    && chown -R django:django /app \
    && ln -s /usr/bin/python3 /usr/bin/python

USER django

ENTRYPOINT ["/entrypoint.sh"]

CMD ["inv", "run", "--gunicorn", "--migrate", "--assets"]
