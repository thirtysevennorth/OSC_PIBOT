#!/usr/bin/bash

# Shared
export PIHUB_OSC_IP="192.168.0.32"
export PIHUB_OSC_PORT="1337"
export PIBOT_OSC_PORT="1338"
#chenged to go to hub temp set to send pihub data to isadora. planned pihub ip .122 and port of 1338

# Automatic
export MY_NAME=$HOSTNAME
export MY_IP=$(ip addr show wlan0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)

# To be set manually as needed
export MY_ID=2
export MY_ROBOT_NAME="irobot2"
