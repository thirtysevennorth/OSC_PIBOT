#!/usr/bin/bash

# Shared
export PIHUB_OSC_IP="192.168.0.32"
export PIHUB_OSC_PORT="1337"
export PIBOT_OSC_PORT="1338"
# changed to go to hub temp set to send hub data to isadora laptop, otherwise planning to set pihub to 192.168.0.122

# Automatic
export MY_NAME=$HOSTNAME
export MY_IP=$(ip addr show wlan0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)

# To be set manually as needed
export MY_ID=1
export MY_ROBOT_NAME="irobot1"
