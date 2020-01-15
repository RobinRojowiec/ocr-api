#!/usr/bin/env bash

# build image
docker build . -t ocr-api

# run image detached
docker run -d -p 8000:8000 ocr-api

