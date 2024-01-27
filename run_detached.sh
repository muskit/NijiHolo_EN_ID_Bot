#!/bin/bash

mkdir -p run
docker build -t nijiholo_bot .
docker run -v ./run:/app/run --name bot --rm -d nijiholo_bot
