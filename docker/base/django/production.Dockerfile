FROM ejplatform/ej-server:base

WORKDIR /app

COPY ./requirements/production.txt /app/requirements/production.txt

RUN pip install -r requirements/production.txt \
    && pip install invoke
