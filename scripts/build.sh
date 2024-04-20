#!/bin/sh

CURPATH="$(dirname `realpath "$0"`)/.."
sudo docker build -t nijiholo_bot "$CURPATH"
sudo docker container create -v "$CURPATH/run:/app/run" --name bot nijiholo_bot
