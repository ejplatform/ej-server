FROM ejplatform/ej-server:latest

USER root

ENV FAKE_DB=true

RUN pip install -r /dependencies/develop.txt

CMD ["/runserver.sh"]
