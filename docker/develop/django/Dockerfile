FROM ejplatform/ej-server:master

USER root

EXPOSE 8000

ENV FAKE_DB=true

RUN pip install -r /dependencies/develop.txt

CMD ["/runserver.sh"]
