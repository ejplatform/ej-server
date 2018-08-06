FROM docker:latest

RUN apk add python3 \
 && python3 -m pip install invoke~=0.23 pip~=18.0 setuptools>=0.31 \
 && ln -s /bin/sh /bin/bash \
 && rm -rf /var/cache/apk/* \
 && rm -rf /root/.cache/*
