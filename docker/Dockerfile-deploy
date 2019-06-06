ARG ORG=ej
FROM ${ORG}/web:base

# Copy files
USER django
COPY --chown=django:django ./.coveragerc /app/
COPY --chown=django:django ./*.py /app/
COPY --chown=django:django ./*.rst /app/
COPY --chown=django:django ./etc/ /app/etc/
COPY --chown=django:django ./docs/ /app/docs
COPY --chown=django:django ./locale/ /app/locale/
COPY --chown=django:django ./lib/ /app/lib/
COPY --chown=django:django ./src/ /app/src/

# Prepare assets
RUN mkdir -p local/logs local/static/ local/media/ local/db/ lib/build/ \
 && inv -e docs \
 && inv -e sass \
 && echo "COLLECTED STATIC ASSETS"
RUN inv -e js \
 && python manage.py collectstatic --noinput \
 && echo "COLLECTED STATIC ASSETS"

# Default command
CMD ["db", "-m", "gunicorn"]
