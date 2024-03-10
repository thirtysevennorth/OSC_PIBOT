#!/usr/bin/env python3
import os
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer #, BlockingOSCUDPServer
from pibot_env import *
from pibot_commands import *
from pibot_utils import *
import pibot_status
import sys
# Pihub

# Send messages like this:
# pihub_osc_client.send_message("/some/address", 123)   # Send float message
# pihub_osc_client.send_message("/some/address", [1, 2., "hello"])  # Send message with int, float and string

pibot_server = None
server_transport = None

async def pibot_start_osc_server_listening():
    global pibot_server
    global server_transport
    success = False
    debug("Creating OSC Server...")
    pibot_server = AsyncIOOSCUDPServer((pibot_server_ip, pibot_server_port), dispatcher, asyncio.get_event_loop())

    # while True:
    try:
        # Serve forever
        info(f"Attempting to spin OSC server, starting to serve forever at ip={pibot_server_ip} and port={pibot_server_port}.")
        server_transport, protocol = await pibot_server.create_serve_endpoint()
    except Exception as e:
        wait_dur = 2
        warn(f"Could not start OSC server with ip={pibot_server_ip} and port={pibot_server_port} - exiting.")
        error(str(e))
        sys.exit(1)
        # await asyncio.sleep(wait_dur)

# NOTE this one keeps trying in a loop
# async def pibot_start_osc_server_listening():
#     global pibot_server
#     global server_transport
#     success = False
#     debug("Creating OSC Server...")
#     pibot_server = AsyncIOOSCUDPServer((pibot_server_ip, pibot_server_port), dispatcher, asyncio.get_event_loop())
#     while True:
#         try:
#             # Serve forever
#             info(f"Attempting to spin OSC server, starting to serve forever at ip={pibot_server_ip} and port={pibot_server_port}.")
#             server_transport, protocol = await pibot_server.create_serve_endpoint()
#         except Exception as e:
#             wait_dur = 2
#             error(f"Could not start OSC server with ip={pibot_server_ip} and port={pibot_server_port} - waiting for {wait_dur}s and retrying...")
#             await asyncio.sleep(wait_dur)
#             # error(str(e))
#             sys.exit(1)

#### OSC
# Sync Handlers
# (handlers that don't need to add anything to an action q)
def default_handler(address, *args):
    # pass
    # FIXME uncomment
    debug(f"DEFAULT OSC HANDLER received:\n Addr: {address}, args: {args}")

def split_args(arglist):
    return split_list_on_empty_string(arglist)

def add_command_list_to_q(command_list):
    # result = []
    for command in command_list:
        f_name = command[0]
        if not isinstance(f_name, str):
            error(f"First element in received command is {f_name}, which is not a string - ignoring.")
            continue
        else:
            f_name = f_name.replace('-', '_').lower() + "_handler"
            f = globals().get(f_name)
            if not f:
                error(f"Command with name {f_name} was not found, aborting...")
                continue
            args = command[1:]
            # Call handler with the appropriate arguments (first is address, which we don't care about),
            # which will in turn schedule the coroutine
            f(None, my_id, *args)
    debug("Added commands to queue.")

def command_list_handler(address, *args):
    debug("command list handler")
    bot_id = args[0]
    if bot_id == -1 or bot_id == my_id:
        command_list = split_args(args[1:])
        add_command_list_to_q(command_list)

# added LED2 (r2, g2, b2, w2), LED 3 (r3, g3, b3, w3) and secondary 5v PWM control (pwm1, pwm2, pwm3, pwm4), and edited set_led function to match
def set_led_handler(address, *args):
    bot_id = args[0]
    if bot_id == -1 or bot_id == my_id:
        r = args[1]
        g = args[2]
        b = args[3]
        w = args[4]
        r2 = args[5]
        g2 = args[6]
        b2 = args[7]
        w2 = args[8]
        pwm1 = args[9]
        pwm2 = args[10]
        pwm3 = args[11]
        pwm4 = args[12]
        r3 = args[13]
        g3 = args[14]
        b3 = args[15]
        w3 = args[16]

        set_led(r, g, b, w, r2, g2, b2, w2, pwm1, pwm2, pwm3, pwm4,r3, g3, b3, w3)
# def set_movement_speed_handler(address, *args):
#     global param_movement_speed
#     bot_id = args[0]
#     if bot_id == -1 or bot_id == my_id:
#         # print("Setting LED...")
#         # print(args)
#         new_val = args[1]
#         info(f"Setting movement speed to {new_val}")
#         param_movement_speed = new_val

# def set_rotation_speed_handler(address, *args):
#     global param_rotation_speed
#     bot_id = args[0]
#     if bot_id == -1 or bot_id == my_id:
#         # print("Setting LED...")
#         # print(args)
#         new_val = args[1]
#         info(f"Setting rotation speed to {new_val}")
#         param_rotation_speed = new_val

# def set_speed_factor_handler(address, *args):
#     global param_speed_factor
#     bot_id = args[0]
#     if bot_id == -1 or bot_id == my_id:
#         val = args[1]
#         info(f"Changing speed factor from {param_speed_factor} to {val}.")
#         param_speed_factor = val

# def set_rotation_speed_factor_handler(address, *args):
#     global param_rotation_speed_factor
#     bot_id = args[0]
#     if bot_id == -1 or bot_id == my_id:
#         val = args[1]
#         info(f"Changing rotation speed factor from {param_rotation_speed_factor} to {val}.")
#         param_rotation_speed_factor = val

# def set_rotation_speed_offset_handler(address, *args):
#     global param_rotation_speed_offset
#     bot_id = args[0]
#     if bot_id == -1 or bot_id == my_id:
#         val = args[1]
#         print(f"Changing rotation speed factor from {param_rotation_speed_offset} to {val}.")
#         param_rotation_speed_offset = val

# Async Handlers
def move_handler(address, *args):
    # global is_docked
    print(f"(handler) is_docked: {pibot_status.is_docked}")
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            distance = args[1] # NOTE it's in cm
            speed = args[2] # NOTE it's in cm/s
            coroutine = move(distance, speed)
            add_to_q(coroutine)

def play_note_handler(address, *args):
    bot_id = args[0]
    if bot_id == -1 or bot_id == my_id:
        freq = args[1]
        coroutine = play_note(freq)
        add_to_q(coroutine)

def rotate_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            degrees = args[1]
            speed = args[2]
            coroutine = rotate(degrees, speed)
            add_to_q(coroutine)

def spin_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            direction = args[1]
            wheel_speed = args[2]
            dur = args[3]
            coroutine = spin(direction, wheel_speed, dur)
            add_to_q(coroutine)

def spin_left_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            wheel_speed = args[1]
            dur = args[2]
            coroutine = spin_left(wheel_speed, dur)
            add_to_q(coroutine)

def spin_right_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            wheel_speed = args[1]
            dur = args[2]
            coroutine = spin_right(wheel_speed, dur)
            add_to_q(coroutine)

def rotate_builtin_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            degrees = args[1]
            coroutine = rotate_builtin(degrees)
            add_to_q(coroutine)

def rotate_with_radius_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            degrees = args[1]
            speed = args[2]
            rad = args[3]
            coroutine = rotate(degrees, speed, rad)
            add_to_q(coroutine)

def navigate_to_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            x = args[1]
            y = args[2]
            if len(args) == 4:
                speed = args[3]
                coroutine = navigate_to(x, y, speed)
            else:
                coroutine = navigate_to(x, y)
            add_to_q(coroutine)

def set_wheel_speeds_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            left = args[1]
            right = args[2]
            coroutine = set_wheel_speeds(left, right)
            add_to_q(coroutine)

def undock_handler(address, *args):
    if not pibot_status.busy_charging:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            coroutine = undock()
            add_to_q(coroutine)
    else:
        warn("Was asked to undock while I'm still busy charging, ignoring.")

def dock_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            coroutine = dock()
            add_to_q(coroutine)

def dock_after_this_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            if len(args) == 1:
                wait_time = -1
            else:
                wait_time = args[1]
                coroutine = dock_after_this()
                add_to_q(coroutine)

def dock_asap_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            if len(args) == 1:
                wait_time = -1
            else:
                wait_time = args[1]
                coroutine = dock_asap(wait_time)
                add_to_q(coroutine)

def face_angle_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            target_angle = args[1]
            rotation_speed = args[2]
            coroutine = face_angle(target_angle, rotation_speed)
            add_to_q(coroutine)
            # FIXME are these needed?
            # # print("Setting LED...")
            # # print(args)
            # new_val = args[1]
            # print(f"Setting rotation speed to {new_val}")
            # param_rotation_speed = new_val

def callibrate_rotation_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            coroutine = callibrate_rotation()
            add_to_q(coroutine)

def set_wheel_speeds_dur_handler(address, *args):
    if not pibot_status.busy_charging and not pibot_status.is_docked:
        bot_id = args[0]
        if bot_id == -1 or bot_id == my_id:
            left = args[1]
            right = args[2]
            dur = args[3]
            coroutine = set_wheel_speeds_dur(left, right, dur)
            add_to_q(coroutine)

## UTILS
def stop_handler(address, *args):
    bot_id = args[0]
    if bot_id == -1 or bot_id == my_id:
        asyncio.run_coroutine_threadsafe(stop_and_empty_q(), asyncio.get_event_loop())

def stop_and_clear_queue_handler(address, *args):
    bot_id = args[0]
    if bot_id == -1 or bot_id == my_id:
        asyncio.run_coroutine_threadsafe(stop_and_empty_q(), asyncio.get_event_loop())

## INFO handlers
def print_pos_handler(address, *args):
    bot_id = args[0]
    if bot_id == -1 or bot_id == my_id:
        coroutine = print_pos()
        add_to_q(coroutine)

def print_battery_handler(address, *args):
    bot_id = args[0]
    if bot_id == -1 or bot_id == my_id:
        coroutine = print_battery()
        add_to_q(coroutine)

def print_dock_status_handler(address, *args):
    bot_id = args[0]
    if bot_id == -1 or bot_id == my_id:
        coroutine = print_dock_status()
        add_to_q(coroutine)

def get_battery_handler(address, *args):
    bot_id = args[0]
    if bot_id == -1 or bot_id == my_id:
        coroutine = get_battery()
        add_to_q(coroutine)

def reset_pos_handler(address, *args):
    bot_id = args[0]
    if bot_id == -1 or bot_id == my_id:
        coroutine = reset_pos()
        add_to_q(coroutine)

def wait_handler(address, *args):
    bot_id = args[0]
    if bot_id == -1 or bot_id == my_id:
        dur = args[1]
        coroutine = wait(dur)
        add_to_q(coroutine)

def speak_handler(address, *args):
    bot_id = args[0]
    if bot_id == -1 or bot_id == my_id:
        s = args[1]
        info(f"Saying: {s}")
        coroutine = speak(s)
        add_to_q(coroutine)

## DISPATCHER STUFF
dispatcher = Dispatcher()
dispatcher.set_default_handler(default_handler)
## COMMAND LISTS
dispatcher.map("/pibot/command/command-list", command_list_handler)
## MOVEMENT
# distance (cm), optional: speed (cm/s)
dispatcher.map("/pibot/command/move", move_handler)
# x, y (cm), optional: speed (cm/s)
dispatcher.map("/pibot/command/navigate-to", navigate_to_handler)
# degrees, optional: speed (degrees/s)
dispatcher.map("/pibot/command/rotate", rotate_handler)
# direction (either "left" or "right"), wheel speed (cm/s), duration
dispatcher.map("/pibot/command/spin", spin_handler)
# wheel speed (cm/s), duration
dispatcher.map("/pibot/command/spin-left", spin_left_handler)
# wheel speed (cm/s), duration
dispatcher.map("/pibot/command/spin-right", spin_right_handler)
# nothing
dispatcher.map("/pibot/command/stop", stop_handler)
dispatcher.map("/pibot/command/stop-and-clear-queue", stop_and_clear_queue_handler)
## UTILITIES
# FIXME update args
# r, g, b, w (16-bit)
dispatcher.map("/pibot/command/set-LED", set_led_handler)
# freq (Hz), optional: duration (s) TODO dur
dispatcher.map("/pibot/command/play-note", play_note_handler)
# nothing
dispatcher.map("/pibot/command/undock", undock_handler)
# dock after you finish everything in the queue
dispatcher.map("/pibot/command/dock", dock_handler)
# dock as soon as you finish the current action in the queue
dispatcher.map("/pibot/command/dock-after-this", dock_after_this_handler)
# dock as soon as you finish the current action in the queue
dispatcher.map("/pibot/command/dock-asap", dock_asap_handler)
# nothing
dispatcher.map("/pibot/command/reset-pos", reset_pos_handler)
# left_speed, right_speed (both cm/s)
dispatcher.map("/pibot/command/set-wheel-speeds", set_wheel_speeds_handler)
# left_speed, right_speed (both cm/s), duration (s)
dispatcher.map("/pibot/command/set-wheel-speeds-dur", set_wheel_speeds_dur_handler)
# nothing
dispatcher.map("/pibot/command/callibrate-rotation", callibrate_rotation_handler)
# string
dispatcher.map("/pibot/command/speak", speak_handler)
dispatcher.map("/pibot/command/wait", wait_handler)
## INFO - these expect nothing
dispatcher.map("/pibot/info/print-pos", print_pos_handler)
dispatcher.map("/pibot/info/print-battery", print_battery_handler)
dispatcher.map("/pibot/info/print-dock-status", print_dock_status_handler)
## PARAMETERS - these expect a single number
# dispatcher.map("/pibot/set/speed-factor", set_speed_factor_handler)
# dispatcher.map("/pibot/set/rotation-speed-factor", set_rotation_speed_factor_handler)
# dispatcher.map("/pibot/set/rotation-speed-offset", set_rotation_speed_offset_handler)
# dispatcher.map("/pibot/set/movement-speed", set_movement_speed_handler)
# dispatcher.map("/pibot/set/rotation-speed", set_rotation_speed_handler)
# dispatcher.map("/pibot/set/rotation-radius", set_rotation_radius_handler)
# dispatcher.map("/pibot/print/rotation-radius", print_rotation_radius_handler)

# dispatchers for dev purposes (quicker to type)

dispatcher.map("/move", move_handler)
# x, y (cm), optional: speed (cm/s)
dispatcher.map("/navigate-to", navigate_to_handler)
# degrees, optional: speed (degrees/s)
dispatcher.map("/rotate", rotate_handler)
dispatcher.map("/rotate-builtin", rotate_builtin_handler)
dispatcher.map("/rotate-with-radius", rotate_with_radius_handler)
# nothing
dispatcher.map("/stop", stop_handler)
## UTILITIES
# r, g, b, w (16-bit)
dispatcher.map("/set-LED", set_led_handler)
# freq (Hz), optional: duration (s) TODO dur
dispatcher.map("/play-note", play_note_handler)
# nothing
dispatcher.map("/undock", undock_handler)
# nothing
dispatcher.map("/dock", dock_handler)
# nothing
dispatcher.map("/dock-asap", dock_asap_handler)
dispatcher.map("/dock-after-this", dock_after_this_handler)
# nothing
dispatcher.map("/reset-pos", reset_pos_handler)
# left_speed, right_speed (both cm/s)
dispatcher.map("/set-wheel-speeds", set_wheel_speeds_handler)
# left_speed, right_speed (both cm/s), duration (s)
dispatcher.map("/set-wheel-speeds-dur", set_wheel_speeds_dur_handler)
# nothing
dispatcher.map("/callibrate-rotation", callibrate_rotation_handler)
# string
dispatcher.map("/speak", speak_handler)
## INFO - these expect nothing
dispatcher.map("/print-pos", print_pos_handler)
dispatcher.map("/get-battery", get_battery_handler)
## PARAMETERS - these expect a single number
# dispatcher.map("/set-speed-factor", set_speed_factor_handler)
# dispatcher.map("/set-rotation-speed-factor", set_rotation_speed_factor_handler)
# dispatcher.map("/set-rotation-speed-offset", set_rotation_speed_offset_handler)
# dispatcher.map("/set-movement-speed", set_movement_speed_handler)
# dispatcher.map("/set-rotation-speed", set_rotation_speed_handler)
# dispatcher.map("/set-rotation-radius", set_rotation_radius_handler)
# dispatcher.map("/face-angle", face_angle_handler)
# dispatcher.map("/print-rotation-radius", print_rotation_radius_handler)

# command to crash on purpose, for testing purposes
def raise_exception_handler(address, *args):
    add_to_q(raise_exception())

dispatcher.map("/raise-exception", raise_exception_handler)

def crash_handler(address, *args):
    global server_transport
    server_transport.close()
    add_to_q(crash())

dispatcher.map("/crash", crash_handler)
