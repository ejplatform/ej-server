FROM ejplatform/python:buster

# We use a different prefix in order to reuse this layer in the dev container
# Set environment variables in order for this to work :)
ENV PATH=$PATH:/pypackages/bin
ENV PYTHONPATH=$PYTHONPATH:/pypackages/lib/python3.6/site-packages

# Install Python dependencies
COPY "./requirements-production.txt" requirements.txt
COPY "./requirements-local.txt" local.txt
RUN pip install -r requirements.txt --prefix /pypackages \
 && rm -rf /root/.cache/*
