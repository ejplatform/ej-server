#!/bin/sh

printf "\n## Updating Base Images\n\n"

if test -n "${git show | grep "update image <base>"}"; then
  printf "\nPerforming Login on Docker.Hub:\n\n"
  docker login -u $DOCKER_HUB_USER -p $DOCKER_HUB_PASS
  printf "\nPushing Base Image:\n\n"
  docker-compose -f ./docker/base/base.build.yml push
  printf "\nPushing Test Image:\n\n"
  docker-compose -f ./docker/base/test.build.yml push
  printf "\nPushing Production Image:\n\n"
  docker-compose -f ./docker/base/production.build.yml push
elif test -n "${git show | grep "update image <base-test>"}"; then
  printf "\nPerforming Login on Docker.Hub:\n\n"
  docker login -u $DOCKER_HUB_USER -p $DOCKER_HUB_PASS
  printf "\nPushing Test Image:\n\n"
  docker-compose -f ./docker/base/test.build.yml push
elif test -n "${git show | grep "update image <base-production>"}"; then
  printf "\nPerforming Login on Docker.Hub:\n\n"
  docker login -u $DOCKER_HUB_USER -p $DOCKER_HUB_PASS
  printf "\nPushing Production Image:\n\n"
  docker-compose -f ./docker/base/production.build.yml push
else
  printf "\nUpdate base images is not necessary.\n\n"
fi
