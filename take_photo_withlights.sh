#!/bin/bash

SAVE_DIR="/mnt/synology/public/greenhousetimelapse"
PHOTO_CMD="sudo rpicam-jpeg --verbose=0 --immediate --nopreview --output"

# Turn on light relay, then photo, then turn off light.
sudo pinctrl set 22 dh
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="${SAVE_DIR}/photo_${TIMESTAMP}.jpg"
${PHOTO_CMD} ${OUTPUT_FILE} --timeout 200
sudo pinctrl set 22 dl
