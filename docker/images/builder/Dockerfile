FROM ejplatform/invoke:latest

# Install stable Debian dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        bundler \
        curl \
        git \
        gnupg2 \
        gettext \
        nodejs \
        ruby-sass \
 # Install yarn
 && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
 && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
 && apt-get update && apt-get install -y --no-install-recommends \
        yarn \
 # Python tools
 && pip install \
        flake8~=3.5.0 \
 # Clean the mess
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /root/.cache/* \
 && echo "INSTALLATION IS DONE!"
