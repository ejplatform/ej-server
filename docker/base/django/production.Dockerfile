FROM ejplatform/ej-server:base

COPY ./requirements/production.txt /dependencies/production.txt

RUN pip install -r /dependencies/production.txt
