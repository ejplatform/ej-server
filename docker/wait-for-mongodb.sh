#!/bin/bash
# wait-for-mongodb.sh

cmd="mongo  mongo/rocketchat initial_script.js"

while ! curl http://mongo:27017/
do
  echo "$(date) - still trying to connect on mongodb"
  sleep 1
done
echo "$(date) - connected successfully"
exec $cmd
