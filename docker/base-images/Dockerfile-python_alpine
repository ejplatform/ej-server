FROM alpine:latest

# Set environment variables
ENV LANG=C.UTF-8

# Install stable Debian dependencies
RUN apk add python3 bash \
 && python3 -m pip install invoke~=1.0 pip~=18.0 flake8~=3.5.0 \
 && ln -s /usr/bin/python3 /usr/bin/python \
 && pip install setuptools==40.0 \
 && rm -rf /root/.cache/* \
 && rm -rf /var/cache/apk/* \
 && echo "INSTALLATION IS DONE!"
