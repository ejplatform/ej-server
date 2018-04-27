FROM ejplatform/ej-server:base

WORKDIR /app

COPY ./requirements/test.txt /app/requirements/test.txt

RUN pip install -r requirements/test.txt
