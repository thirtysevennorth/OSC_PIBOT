#!/usr/bin/env python3

from pibot_env import *

from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, Robot, Create3
from irobot_edu_sdk.music import Note

# Robot instance (Bluetooth)
robot = Create3(Bluetooth(my_robot_name))
