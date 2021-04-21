#!/usr/bin/env bash

# load poetry virtualenv
echo "source $(poetry env info --path)/bin/activate" >> /root/.bashrc
source $(poetry env info --path)/bin/activate

# prepare database
inv db
inv db-assets

# install js dependencies
(cd lib && npm i && inv build-assets)

# compile sass files
inv sass

# generate translations
inv i18n
inv i18n --compile

# generates documentation
inv docs

# runs django collectstatic command
inv collect

# runs develop server
inv run
