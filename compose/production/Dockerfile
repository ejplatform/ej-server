FROM python:3.5 as django

ENV PYTHONUNBUFFERED 1

RUN groupadd -r django \
    && useradd -r -g django django

# Requirements have to be pulled and installed here, otherwise caching won't work
COPY ./requirements /requirements
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY ./compose/production/django/gunicorn.sh /gunicorn.sh
RUN sed -i 's/\r//' /gunicorn.sh
RUN chmod +x /gunicorn.sh
RUN chown django /gunicorn.sh

COPY ./compose/production/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r//' /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN chown django /entrypoint.sh

COPY . /app

RUN mkdir /app/staticfiles

RUN export $(cat /app/env.example | grep -v ^# | xargs) && \
    python /app/manage.py collectstatic --noinput

RUN chown -R django /app

USER django

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]
CMD ["/gunicorn.sh"]


FROM nginx:1.13 as nginx

COPY ./compose/production/nginx/default.conf /etc/nginx/conf.d/default.conf
COPY --from=django /app/staticfiles/static/ /usr/share/nginx/html/static/
