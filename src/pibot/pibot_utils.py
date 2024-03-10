#!/usr/bin/env python3
import datetime
import os
import math
import asyncio
from queue import Queue
from asyncio import Lock
import sys
import threading

## LOGGING
def now_formatted():
    return datetime.datetime.now().strftime("%d/%m/%y, %H:%M:%S")

def format_log_msg(type, msg):
    return f"[{now_formatted()}] [{type}]: {msg}"

# log_file = os.getenv("PIHUB_LOG_FILE")
log_dir = os.path.join('.', "log")
os.makedirs(log_dir, exist_ok=True)
log_file = open(os.path.join(log_dir, "main.txt"), 'a')

def main_log(type, msg):
    # Write the line to the file
    log_file.write(format_log_msg(type, msg) + '\n')
    log_file.flush()

def make_logger(type):
    log_file_path = os.path.join(log_dir, type.lower() + '.txt')
    def log_msg(msg):
        log_line = format_log_msg(type, msg)
        # print to stdout
        print(log_line)
        # append to type-specific log
        with open(log_file_path, "a") as log_file:
            log_file.write(log_line + '\n')
            log_file.flush()

    return log_msg

info = make_logger("INFO")
warn = make_logger("WARN")
error = make_logger("ERROR")
debug = make_logger(">>DEBUG>>")

## ASYNCIO
# This is your list of coroutines

## MATHS
def calculate_arc_length(radius, angle_in_degrees):
    # Convert angle from degrees to radians
    angle_in_radians = math.radians(angle_in_degrees)
    # Calculate the arc length
    arc_length = angle_in_radians * radius

    print(f"Arc length:\nrad: {radius}, angle: {angle_in_degrees}, arc_length: {arc_length}")
    return arc_length

def points_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def wheel_speed_for_rotation(R, W):
    """
    Calculate the linear speed of a point rotating around a circle.

    :param R: Radius of the circle in centimeters.
    :param W: Angular speed in degrees per second.
    :return: Linear speed in cm/s.
    """
    return R * W * math.pi / 180


def normalize_angle(angle):
    """ Normalize the angle to be within 0 to 359 degrees. """
    return angle % 360


def calculate_delta_angle(current_angle, target_angle):
    """
    Calculate the delta angle required to turn from current_angle to target_angle.

    :param current_angle: Current angle in degrees
    :param target_angle: Target angle in degrees
    :return: Delta angle in degrees, positive for clockwise and negative for counter-clockwise
    """
    delta = target_angle - current_angle
    if delta > 180:
        delta -= 360
    elif delta < -180:
        delta += 360
    return -delta  # Inverting the sign to match the specified behavior

def min_angle_difference(angle1, angle2):
    # Normalize angles to [0, 360) range
    angle1 = angle1 % 360
    angle2 = angle2 % 360

    # Calculate absolute difference
    diff = abs(angle1 - angle2)

    # If the difference is greater than 180, find the minimum difference
    if diff > 180:
        diff = 360 - diff

    return diff

def offset_pos(x, y, angle, distance):
    # Convert angle from degrees to radians
    radians = math.radians(angle)
    # Calculate new coordinates
    x_new = x + distance * math.cos(radians)
    y_new = y + distance * math.sin(radians)

    return x_new, y_new

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

## CALLIBRATIONS
import json

min_supported_rotation_speed = 15
max_supported_rotation_speed = 40
supported_rotation_speeds = range(min_supported_rotation_speed,
                                  max_supported_rotation_speed + 1)
wheel_radius = 11.75

default_rotation_speeds_dict = {rotation_speed: wheel_speed_for_rotation(11.5, rotation_speed)
                               for rotation_speed in supported_rotation_speeds}

path_to_rotation_speeds_dict = "rotation_callibration.json"

def read_rotation_callibration_dict():
    if os.path.exists(path_to_rotation_speeds_dict):
        with open(path_to_rotation_speeds_dict, 'r') as json_file:
            loaded_data = json.load(json_file)
            int_keys_data = {int(key): value for key, value in loaded_data.items()}
            return int_keys_data
    else:
        warn(f"Could not find rotation speeds dict at path {path_to_rotation_speeds_dict}, returning default one...")
        return default_rotation_speeds_dict

def write_rotation_callibration_dict(d):
    with open(path_to_rotation_speeds_dict, 'w') as json_file:
        json.dump(d, json_file)

rotation_speeds_dict = read_rotation_callibration_dict()

## I2C
# Attempt to import necessary modules for I2C
try:
    import busio
    from board import SCL, SDA
    from adafruit_pca9685 import PCA9685
    i2c_libraries_available = True
    info("I2C packages found, continuing...")
except ImportError:
    warn("I2C packages not found, ignoring I2C...")
    i2c_libraries_available = False

i2c_bus = None
pca = None

# Define setup_i2c function
def setup_i2c():
    if i2c_libraries_available:
        global i2c_bus
        global pca
        try:
            # Create the I2C bus interface and pca instance
            i2c_bus = busio.I2C(SCL, SDA)
            pca = PCA9685(i2c_bus)
            pca.frequency = 240
            info("I2C bus found, set PCA frequency successfully.")
        except ValueError:
            warn("I2C device not found. Please check the connection.")
    else:
        pass  # Do nothing if libraries are not available

# Define set_led function
def set_led(r, g, b, w, r2, g2, b2, w2, pwm1, pwm2, pwm3, pwm4,r3, g3, b3, w3):
    if i2c_libraries_available:
        # Assuming pca is globally accessible or passed as an argument
        # PCA 0-3 LED 1, PCA 4-7 LED 2, PCA 8-11 secondary 5v, PCA 12-15 LED 3 (or for battery charge control or motor control)
        pca.channels[0].duty_cycle = r
        pca.channels[1].duty_cycle = g
        pca.channels[2].duty_cycle = b
        pca.channels[3].duty_cycle = w
        pca.channels[4].duty_cycle = r2
        pca.channels[5].duty_cycle = g2
        pca.channels[6].duty_cycle = b2
        pca.channels[7].duty_cycle = w2
        pca.channels[8].duty_cycle = pwm1
        pca.channels[9].duty_cycle = pwm2
        pca.channels[10].duty_cycle = pwm3
        pca.channels[11].duty_cycle = pwm4
        pca.channels[12].duty_cycle = r3
        pca.channels[13].duty_cycle = g3
        pca.channels[14].duty_cycle = b3
        pca.channels[15].duty_cycle = w3
    else:
        pass  # Do nothing if libraries are not available

## COMMAND Q
command_q = Queue()
command_q_lock = Lock()

async def clear_command_q():
    global command_q
    # await command_q_lock.acquire()  # Acquire the lock before executing the command
    info("Emptying Command Queue")
    command_q = Queue()
    # command_q_lock.release()  # Release the lock after the command is executed

def add_to_q(task):
    # print(f"Adding task to Q: {task}")
    global command_q
    # await command_q_lock.acquire()  # Acquire the lock before executing the command
    command_q.put(task)
    # command_q_lock.release()  # Release the lock after the command is executed


## MISC UTILS
def split_list_on_empty_string(input_list):
    result = []
    current_sublist = []
    for item in input_list:
        if item == "":
            if current_sublist:
                result.append(current_sublist)
                current_sublist = []
        else:
            current_sublist.append(item)
    if current_sublist:
        result.append(current_sublist)

    return result

async def raise_exception():
    raise Exception("HEHEHEHE I BROKEN")

async def crash():
    sys.exit(1)
