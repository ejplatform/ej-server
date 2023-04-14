#!/usr/bin/env bash

# load poetry virtualenv
echo "source $(/root/.local/bin/poetry env info --path)/bin/activate" >> /root/.bashrc
echo "alias poetry=/root/.local/bin/poetry" >> /root/.bashrc
echo "PATH=$PATH:/root/.local/bin" >> /root/.bashrc

poetry=/root/.local/bin/poetry

# prepare database
$poetry run inv db

# install js dependencies
(cd lib && npm i && $poetry inv build-assets)

# compile sass files
$poetry run inv sass

# generate translations
$poetry run inv i18n
$poetry run inv i18n --compile

# generates documentation
$poetry run inv docs

# runs django collectstatic command
$poetry run inv collect

# runs develop server
$poetry run inv run
