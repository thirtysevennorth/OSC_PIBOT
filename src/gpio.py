#!/usr/bin/env python3

# sample code for button press on HUB pi.

from gpiozero import Button
from signal import pause
from pythonosc.udp_client import SimpleUDPClient
from time import sleep

# Set these to the appropriate values
button = Button(4, pull_up=False, bounce_time=1, hold_time=2)
osc_ip = "192.168.0.223"
osc_port = 1234
osc_address = "/isadora/button-pressed"

# Initialize OSC client
osc_client = SimpleUDPClient(osc_ip, osc_port)

def button_pressed():
    print("button was pressed")
    osc_client.send_message(osc_address, 1)  # Send OSC message with value 1

def button_released():
    print("button was released")
    osc_client.send_message(osc_address, 0)  # Send OSC message with value 1

button.when_held = button_pressed

button.when_released = button_released

print("waiting for button presses")
try:
    # Keep the program running
    while True:
        sleep(1)
except KeyboardInterrupt:
    print("Program stopped")

pause()
