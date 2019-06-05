FROM ejplatform/python:buster

# Set environment variables
ENV LANG=C.UTF-8

# Install tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        git \
        gettext \
        ruby-sass \
        xz-utils \
 # Python tools
 && pip install \
        flake8~=3.5.0 \
 # Clean up the mess
 && apt-get autoremove -y \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /root/.cache/* \
 && echo "INSTALLATION IS DONE!"

# Install node from binaries (nodejs package in Buster does not contain npm!)
RUN curl https://nodejs.org/dist/v8.11.3/node-v8.11.3-linux-x64.tar.xz -o node.tar.xz \
 && tar -xJf node.tar.xz \
 && mv node-v8.11.3-linux-x64 node \
 && mv /node/bin/* /usr/bin/ \
 && mv /node/lib/node_modules /usr/lib \
 && mv /node/include/node /usr/include \
 # Install global npm packages
 && npm install -g \
        yarn \
        webpack@4.6.0 \
 && rm -rf node* \
 && echo "NPM INSTALLATION IS DONE!"
