#!/bin/sh

printf "\n## Building Base Images\n\n"

if [ -n "`git show | grep "build image <base>"`" ]; then
  printf "\nBuilding Base Image:\n\n"
  docker-compose -f ./docker/base/base.build.yml build
  printf "\nBuilding Test Base Image:\n\n"
  docker-compose -f ./docker/base/test.build.yml build
  printf "\nBuilding Production Base Image:\n\n"
  docker-compose -f ./docker/base/production.build.yml build
elif [ -n "`git show | grep "build image <base-test>"`" ]; then
  printf "\nBuilding Test Base Image:\n\n"
  docker-compose -f ./docker/base/test.build.yml build
elif [ -n "`git show | grep "build image <base-production>"`" ]; then
  printf "\nBuilding Production Base Image:\n\n"
  docker-compose -f ./docker/base/production.build.yml build
else
  printf "\nBuild base images is not necessary.\n\n"
fi
