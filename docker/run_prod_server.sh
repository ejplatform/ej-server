#!/usr/bin/env bash

# load poetry virtualenv
source $(poetry env info --path)/bin/activate

# prepare database
inv db
inv db-assets

# install js dependencies
cd lib && npm i && inv build-assets

# compile sass files
inv sass

# generate translations
inv i18n --compile
inv i18n

# generates documentation
inv docs

# runs django collectstatic command
inv collect

# runs production server
inv gunicorn
