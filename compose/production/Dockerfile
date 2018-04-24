FROM python:3.6 as django

ENV PYTHONUNBUFFERED 1

RUN groupadd -r django \
    && useradd -r -g django django

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY ./compose/production/django/gunicorn.sh /gunicorn.sh
COPY ./compose/production/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /gunicorn.sh \
    && chmod +x /gunicorn.sh \
    && chown django /gunicorn.sh \
    && sed -i 's/\r//' /entrypoint.sh \
    && chmod +x /entrypoint.sh \
    && chown django /entrypoint.sh

COPY . /app

RUN mkdir /app/staticfiles

WORKDIR /app
USER django

RUN export $(cat /app/env.example | grep -v ^# | xargs) \
    && mkdir /app/local \
    && echo $BUILD >> /app/local/build.info \
    && python /app/manage.py collectstatic --noinput \
    && chown -R django /app \
    && cd /app \
    && inv db-fake --safe

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/gunicorn.sh"]


FROM nginx:1.13 as nginx

COPY ./compose/production/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=django /app/staticfiles/static/ /usr/share/nginx/html/static/
