FROM debian:jessie

LABEL Description="This dockerfile checks if the mongodb server is up."

ADD initial_script.js /initial_script.js
ADD wait-for-mongodb.sh /wait-for-mongodb.sh

RUN apt-get update && apt-get install -y sudo curl mongodb

ENTRYPOINT ["/wait-for-mongodb.sh"]
