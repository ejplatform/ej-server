FROM ejplatform/ej-server:master

USER root

ENV FAKE_DB=true

RUN pip install -r /dependencies/develop.txt

CMD ["/runserver.sh"]
