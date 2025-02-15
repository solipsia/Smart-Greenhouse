#!/bin/bash

# Directory to save photos
SAVE_DIR="/mnt/synology/public/greenhouse"

# Command to take a photo
PHOTO_CMD="sudo rpicam-jpeg --verbose=0 --immediate --nopreview --output"

# Interval between photos in seconds
INTERVAL=58

# Infinite loop to take photos every INTERVAL seconds
while true; do
  # Generate a timestamp
  TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
  
  # Set the output file name with the timestamp
  OUTPUT_FILE="${SAVE_DIR}/photo_${TIMESTAMP}.jpg"
  
  # Take the photo
  ${PHOTO_CMD} ${OUTPUT_FILE} --timeout 200
  
  # Wait for the specified interval before taking the next photo
  sleep ${INTERVAL}
  
  # Find and delete files older than 24 hours
  sudo find ${SAVE_DIR} -name "photo_*.jpg" -type f -mmin +1440 -exec rm {} \;
done
