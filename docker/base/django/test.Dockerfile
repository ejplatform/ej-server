FROM ejplatform/ej-server:base

COPY ./requirements/test.txt /dependencies/test.txt

RUN pip install -r /dependencies/test.txt
