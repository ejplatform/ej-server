#!/usr/bin/env bash
# platform options: linux32, linux64, mac64, win32
if [ "$(uname)" == "Darwin" ]; then
    PLATFORM=mac64
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
  if [ "$(uname -m)" == "x86_64" ]; then
    PLATFORM=linux64
  else
    PLATFORM=linux32
  fi
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ]; then
    PLATFORM=win32
fi
VERSION=$(curl http://chromedriver.storage.googleapis.com/LATEST_RELEASE)
curl http://chromedriver.storage.googleapis.com/$VERSION/chromedriver_$PLATFORM.zip \
    | bsdtar -xvf - -C ${VIRTUAL_ENV}/bin/
chmod +x ${VIRTUAL_ENV}/bin/chromedriver
