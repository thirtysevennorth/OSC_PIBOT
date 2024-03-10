#!/usr/bin/env python3
import os
from pythonosc.udp_client import SimpleUDPClient
from pibot_utils import *

## OSC comms
# Pihub
pihub_ip = str(os.environ["PIHUB_OSC_IP"])
pihub_port = int(os.environ["PIHUB_OSC_PORT"])

pihub_osc_client = SimpleUDPClient(pihub_ip, pihub_port)  # Create client
pihub_client_ready = True

# Isadora
isadora_ip = str(os.environ["ISADORA_OSC_IP"])
isadora_port = int(os.environ["ISADORA_OSC_PORT"])

isadora_osc_client = SimpleUDPClient(isadora_ip, isadora_port)  # Create client
isadora_client_ready = True

# Pibot
pibot_server_ip = os.environ["MY_IP"]
# pibot_server_ip = "127.0.0.1"
info(f"My IP address is: {pibot_server_ip}")
pibot_server_port = os.environ["PIBOT_OSC_PORT"]

# General
my_id = int(os.environ["MY_ID"])
info(f"My ID is: {my_id}")

my_robot_name = os.environ["MY_ROBOT_NAME"]
info(f"My robot is: {my_robot_name}")

def message_servers(address, args):
    pihub_osc_client.send_message(address, args)
    isadora_osc_client.send_message(address, args)
