FROM ejplatform/python:deploy

# Install Python dependencies.
COPY "./requirements-develop.txt" requirements.txt

RUN pip install -r requirements.txt --prefix /pypackages \
 && rm -rf /var/lib/apt/lists/* \
 && rm -rf /root/.cache/* \
 && echo "FINISHED UPDATE"
