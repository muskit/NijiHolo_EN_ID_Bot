#!/bin/sh

mkdir -p run
docker run -v ./run:/app/run --name bot -d nijiholo_bot
