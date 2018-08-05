A simple container that installs Python 3 and invoke in a pre-build docker
image.

Running::

    sudo docker run -it ejplatform/docker-invoke


Building::

    sudo docker build . -t ejplatform/docker-invoke:latest
    sudo docker push ejplatform/docker-invoke:latest

