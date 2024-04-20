#!/bin/sh
CURPATH="$(dirname `realpath "$0"`)/.."
cd "$CURPATH"
mkdir -p run
sudo docker run -v "$CURPATH/run:/app/run" --name bot -it nijiholo_bot
