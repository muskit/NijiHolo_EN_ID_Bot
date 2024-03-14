#!/bin/sh

mkdir -p run
docker run -v ./run:/app/run --name bot -it nijiholo_bot
