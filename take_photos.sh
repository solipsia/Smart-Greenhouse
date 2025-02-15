#!/bin/bash

# Directory to save photos
SAVE_DIR="/mnt/synology/public/greenhouse"

# Command to take a photo
PHOTO_CMD="sudo rpicam-jpeg --verbose=0 --immediate --nopreview --output"

is_file_open() {
  sudo fuser /mnt/synology/public/greenhouse/sensoroverlay.png > /dev/null 2>&1
}

# Infinite loop to take photos at exactly 30 seconds past the minute
while true; do
  # Get the current time
  CURRENT_SECOND=$(date +"%S")
  CURRENT_TIME=$(date +"%H%M%S")

  # Check if the current time is exactly 30 seconds past the minute
  if [ "$CURRENT_SECOND" -eq "30" ]; then
    # Generate a timestamp
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    
    # Set the output file name with the timestamp
    OUTPUT_FILE="${SAVE_DIR}/photo_${TIMESTAMP}.jpg"
    
    # Take the photo
    ${PHOTO_CMD} ${OUTPUT_FILE} --timeout 200

    #wait for overlay to complete
    while is_file_open; do
      echo "File is still being accessed. Waiting..."
      sleep 1  # Wait for 1 second before checking again
    done

    sudo composite -gravity center /mnt/synology/public/greenhouse/sensoroverlay.png ${OUTPUT_FILE} ${OUTPUT_FILE}
    sudo cp ${OUTPUT_FILE} ${SAVE_DIR}/latest.jpg
    
    # Find and delete files older than 24 hours
    sudo find ${SAVE_DIR} -name "photo_*.jpg" -type f -mmin +1440 -exec rm {} \;
    
    # Wait until the next second to avoid multiple photos being taken at the same time
    while [ "$(date +"%S")" -eq "30" ]; do
      sleep 0.1
    done
  fi

  # Check if the current time is exactly 02:00:00 AM
  #if [ "$CURRENT_TIME" == "020000" ]; then
  if [ "$CURRENT_TIME" == "020000" ]; then
    /home/pi/take_photo_withlights.sh
    
    # Wait until the next second to avoid running the script multiple times at the same time
    while [ "$(date +"%H%M%S")" == "020000" ]; do
      sleep 0.1
    done
  fi
done
