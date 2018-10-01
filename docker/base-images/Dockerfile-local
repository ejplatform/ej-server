FROM ejplatform/python:test as testpackages
FROM ejplatform/tools:latest

# Install Python dependencies
COPY --from=testpackages /pypackages /pypackages

# Set environment variables in order for this to work :)
ENV PATH=$PATH:/pypackages/bin
ENV PYTHONPATH=$PYTHONPATH:/pypackages/lib/python3.6/site-packages
