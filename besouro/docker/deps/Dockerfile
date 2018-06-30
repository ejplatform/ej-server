FROM besouro/ej-server:base

WORKDIR /dependencies

COPY ./etc/npm_globals.txt /dependencies/npm_globals.txt

RUN < npm_globals.txt xargs yarn global add

COPY ./etc/requirements/*.txt /dependencies/

RUN pip install -r /dependencies/production.txt
RUN pip install -r /dependencies/git-modules.txt
