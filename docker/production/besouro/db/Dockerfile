from postgres

RUN su postgres -c "/usr/lib/postgresql/10/bin/initdb -d /var/lib/postgresql/10/data"
RUN su postgres -c "/usr/lib/postgresql/10/bin/pg_ctl -D /var/lib/postgresql/10/data start"
RUN su postgres -c "createuser -d -l --no-password besouro"
RUN su postgres -c "createdb -O besouro --no-password besouro-local"

