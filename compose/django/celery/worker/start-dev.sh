#!/bin/sh

set -o errexit
set -o nounset
set -o xtrace

celery -A pushtogether.taskapp worker -l INFO
