FROM besouro/ej-server:deps

EXPOSE 8000

ENV FAKE_DB=true

COPY ./etc/requirements/*.txt /dependencies/

RUN pip install -r /dependencies/develop.txt -r /dependencies/git-modules.txt

COPY ./etc/scripts/**/* /

WORKDIR /app

ENTRYPOINT ["/entrypoint.sh"]

CMD ["/runserver.sh"]
