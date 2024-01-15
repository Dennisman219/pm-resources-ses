#!/bin/bash

# must have fswebcam installed
command -v fswebcam >/dev/null 2>&1 || {
  echo "I require fswebcam but it's not installed. Aborting." >&2; exit 1;
}

# must have rsync installed
command -v rsync >/dev/null 2>&1 || {
  echo "I require rsync but it's not installed. Aborting." >&2; exit 1;
}

echo "Taking photo..."

# timestamp for the new file
TIMESTAMP=$(date +%s)

# the output path + filename
IMAGENAME="/home/webcam/images/image-$TIMESTAMP.jpg"

# the size of the screenshot to take
fswebcam -d /dev/video0 -r 640x480 --no-banner -v -S 10 --set brightness=100% --save $IMAGENAME

echo "Saved new file at $IMAGENAME"

echo "Starting rsync..."

# src is the local folder with all the images
SRC="/home/webcam/images/"

# destination location on laptop
DEST="rusudanmachavariani@rusudans-mbp:/Users/rusudanmachavariani/Desktop/dice_test"

# rsync file to remote
rsync --update --archive --delete --recursive --compress --progress --chmod=u=rwx,g=rx,o=rx $SRC $DEST &&
  echo "rsync completed successfully" 1>&2 || echo "rsync ended with errors" >&2

echo "Starting MSP transfer..."

python transfer.py $IMAGENAME && echo "transfer executed successfully" 1>&2 || echo "transfer ended with errors" >&2

exit 0