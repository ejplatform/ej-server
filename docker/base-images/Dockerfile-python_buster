FROM debian:buster-slim

# Set environment variables
ENV LANG=C.UTF-8

# Install stable Debian dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3.6 \
        python3-pip \
        ruby-sass \
        python3-setuptools \
        unzip \
 && pip3 install --upgrade pip setuptools invoke~=0.23 \
 && ln -s /usr/bin/python3 /usr/bin/python \
 && ln -s /usr/bin/pip3 /usr/bin/pip \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /root/.cache/* \
 && echo "INSTALLATION IS DONE!"
