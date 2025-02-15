#!/bin/bash

# Function to check network connectivity
check_network() {
    # Check if we can reach a reliable website (like Google)
    if ping -c 1 -W 1 google.com >/dev/null 2>&1; then
        return 0 # Network is up
    else
        return 1 # Network is down
    fi
}

# Wait until the network is up
until check_network; do
    echo "$(date '+%Y-%m-%d %H:%M:%S') Waiting for network..."
    sleep 1
done

echo "$(date '+%Y-%m-%d %H:%M:%S') Network is up."

