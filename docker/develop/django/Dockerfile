FROM ejplatform/ej-server:master

USER root

EXPOSE 8000

ENV FAKE_DB=true

COPY ./etc/requirements/*.txt /dependencies/
RUN pip install -r /dependencies/develop.txt -r /dependencies/git-modules.txt

CMD ["/runserver.sh"]
