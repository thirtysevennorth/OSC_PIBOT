#!/usr/bin/env python3
# from irobot_edu_sdk.backend.bluetooth import Bluetooth
# from irobot_edu_sdk.robots import event#, Robot, Create3
# from irobot_edu_sdk.music import Note
import os
from pibot_utils import *
# from pibot_osc import *
from pibot_env import *
from pibot_backend import *
from pibot_status import *
import pibot_status

## PARAMS
param_speed_factor = 1.0
param_rotation_speed_factor = 1.0
param_rotation_speed_offset = 0.0
param_movement_speed = 7
param_rotation_speed = 14
wheel_width = 1.30  # in cm
distance_between_outer_edges = 24.75  # in cm
rotation_radius = (distance_between_outer_edges - wheel_width) / 2

# Executors
async def play_note(freq):
    # print(f"Playing note with freq={freq}")
    await robot.play_note(freq, 7)

def line_length(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def calculate_navigation(x1, y1, x2, y2):
    """
    Calculate the angle that the robot should be facing
    and the (straight line) distance it should travel
    to go from point A to point B.
    """
    target_angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
    distance = line_length(x1, y1, x2, y2)
    return target_angle, distance

rotation_speed = 15

async def navigate_to(x, y, speed=6):
    log_msg = f"Navigating to: x={x}, y={y}..."
    main_log("NAV", log_msg)
    debug(log_msg)
    while True:
        if pibot_status.is_docked or pibot_status.quit_all_movement_loops:
            break
        start_pos = await get_pos()
        distance = line_length(start_pos.x, start_pos.y, x, y)
        if distance <= 5:
            log_msg = f"Finished navigating to: x={x}, y={y}."
            main_log("NAV", log_msg)
            debug(log_msg)
            pos = await get_pos()
            return pos
        else:
            target_angle, distance_to_travel = calculate_navigation(start_pos.x, start_pos.y, x, y)
            rotation_result = await face_angle(target_angle, rotation_speed)
            movement_result = await move(distance_to_travel, speed)

async def stop():
    # NOTE perhaps overkill but doesn't hurt to make sure...
    info("Stopping...")
    main_log("STOP", "Stopping.")
    await robot.stop()
    await set_wheel_speeds(0, 0)
    pibot_status.quit_all_movement_loops = True
    await robot.stop()
    await wait(2)
    await set_wheel_speeds(0, 0)
    pibot_status.quit_all_movement_loops = False
    debug("Stop routine finished.")

async def stop_and_empty_q():
    main_log("STOP", "Stopping and emptying queue.")
    await clear_command_q()
    await stop()

async def get_pos():
    pos = await robot.get_position()
    return pos

async def print_pos():
    pos = await get_pos()
    info(pos)

async def get_battery():
    try:
        bat = await robot.get_battery_level()
        return bat
    except EOFError as e:
        error(f"Caught EOFError while trying to get battery level:/n{e}")
        return None
    except Exception as e:
        error(f"Caught an unexpected exception while asking robot for battery level:/n{e}")
        return None

async def move_ramp_speed(distance, speeds_and_durs):
    start_pos = await get_pos()

async def move(distance_cm, speed_cms):
    debug(f"Moving forward by {distance_cm}cm at a speed of {speed_cms}cm...")
    dur = distance_cm / speed_cms
    adjusted_speed = speed_cms
    result_pos = await set_wheel_speeds_dur(adjusted_speed, adjusted_speed, dur)
    return result_pos

async def rotate_builtin(direction, degrees):
    await robot.turn(direction, degrees)

async def rotate(degrees, degrees_per_s=15):
    if degrees_per_s < min_supported_rotation_speed or degrees_per_s > max_supported_rotation_speed:
        warn(f"Rotational speed of {degrees_per_s} degrees/s is out of the supported range (min: {min_supported_rotation_speed}, max: {max_supported_rotation_speed}) - clamping.")
        degrees_per_s = clamp(degrees_per_s, min_supported_rotation_speed, max_supported_rotation_speed)

    start_pos = await get_pos()
    info(f"Rotating {degrees} degrees at a speed of {degrees_per_s} d/s...")
    debug(f"Starting position: {start_pos}")

    if degrees == 0:
        return
    elif degrees > 0:
        direction = 'right'
    else:
        direction = 'left'

    degrees = abs(degrees)
    wheel_speed = rotation_speeds_dict[degrees_per_s] #calculate_wheel_speed_for_rotation(degrees, degrees_per_s)
    # wheel_speed = (wheel_speed * param_rotation_speed_factor) + param_rotation_speed_offset
    rotation_dur = degrees / degrees_per_s

    if direction == 'right':
        speed_l = wheel_speed
        speed_r = -wheel_speed
    elif direction == 'left':
        speed_l = -wheel_speed
        speed_r = wheel_speed

    result = await set_wheel_speeds_dur(speed_l, speed_r, rotation_dur)

async def spin(direction, wheel_speed, dur):
    if direction == 'left':
        speed_l = -wheel_speed
        speed_r = wheel_speed
    else:
        speed_l = wheel_speed
        speed_r = -wheel_speed

    await set_wheel_speeds_dur(speed_l, speed_r, dur)

async def spin_left(wheel_speed, dur):
    await spin('left', wheel_speed, dur)

async def spin_right(wheel_speed, dur):
    await spin('right', wheel_speed, dur)

async def undock():
    info("Undocking...")
    main_log("DOCK", "Undocking...")
    message_servers("/pibot/update/undocking", [int(my_id)])

    result = await robot.undock()
    if result and result['status'] == 0:
        info("Undocked successfully.")
        main_log("DOCK", "Undocked successfully.")
        pibot_status.is_docked = False
        message_servers("/pibot/update/undocked", [int(my_id)])
        return result
    else:
        log_msg = f"Undocking failed, result:/n{result}"
        main_log("DOCK ERROR", log_msg)
        warn(log_msg)

async def dock(wait_time=5):
    log_msg = "Starting docking sequence..."
    main_log("DOCK", log_msg)
    info(log_msg)
    message_servers("/pibot/update/docking", [int(my_id)])
    result = await navigate_to(0, -60)
    result = await navigate_to(0, -50)
    debug("Running built-in dock command...")
    result = await robot.dock()
    debug(f"Dock result: {result}")
    if result and result['result'] == 1:
        pibot_status.is_docked = True
        log_msg = "Docking successful, resetting position."
        info(log_msg)
        main_log("DOCK", log_msg)
        message_servers("/pibot/update/docked", [my_id, True])
        await reset_pos()
    else:
        message_servers("/pibot/update/docked", [my_id, False])
        error("Failed to dock.")

async def get_docking_values():
    result = await robot.get_docking_values()
    return result

async def check_docking_contacts():
    docking_values = await get_docking_values()
    return docking_values['contacts'] == 1

async def print_dock_status():
    result = await get_docking_values()
    if result:
        info(result)

async def wait(amt):
    await robot.wait(amt)

async def dock_after_this():
    main_log("DOCK", "Docking as soon as I complete my current command in the queue.")
    await clear_command_q()
    add_to_q(dock())

async def dock_asap():
    main_log("DOCK", "Docking ASAP.")
    await stop_and_empty_q()
    add_to_q(dock())

async def reset_pos():
    await robot.reset_navigation()
    info("Position reset.")
    main_log("POS", "Position reset.")

async def speak(s):
    await robot.say(s)

async def set_wheel_speeds(left, right):
    # print("Setting wheel speeds...")
    await robot.set_wheel_speeds(left, right)

async def set_wheel_speeds_dur(left, right, dur):
    time_to_wait = dur * param_speed_factor
    # print(f"Setting wheel speeds to ({left}, {right}) with wait duration of {dur}s...")
    await robot.set_wheel_speeds(left, right)
    # print(f"Waiting for {dur} seconds...")
    await robot.wait(time_to_wait)
    await robot.set_wheel_speeds(0, 0)
    final_pos = await get_pos()
    return final_pos
    # print(f"Done setting wheel speeds, they've been reset to 0.")

async def face_angle(target_angle, degree_s=15):
    while True:
        if pibot_status.is_docked or pibot_status.quit_all_movement_loops:
            break
        current_pos = await get_pos()
        current_angle = current_pos.heading
        difference = min_angle_difference(current_angle, target_angle)
        if difference < 2:
            debug("Facing angle is close enough, returning...")
            result = await get_pos()
            return result
        else:
            amt_to_turn = calculate_delta_angle(current_angle, target_angle)
            print(f"Turning {amt_to_turn} degrees...")
            await rotate(amt_to_turn, degree_s)

#### CALIBRATIONS
async def callibrate_rotation():
    info(f"Callibrating rotation...")
    # Read speeds from last dict (or use defaults if file not found)
    speeds_dict = read_rotation_callibration_dict()
    debug(f"Starting speeds: {speeds_dict}")
    # Callibrate one pair at a time
    items = reversed(speeds_dict.items())
    for angular_speed, init_wheel_speed in items:
        info(f"-Callibrating for angular speed: {angular_speed}...")
        info(f"-Initial wheel speed: {init_wheel_speed}")
        current_wheel_speed = init_wheel_speed
        # for every angle in the list (start small)
        for target_rotation in [45, 90]:
            info(f"--Current target rotation: {target_rotation}")
            target_rotation_dur = target_rotation / angular_speed
            info(f"--Current target rotation dur: {target_rotation_dur}")
            i = 1
            while True:
                info(f"---angular speed {angular_speed}, iteration {i}...")
                info(f"---Current wheel speed is: {current_wheel_speed}")
                await reset_pos()
                start_pos = await get_pos()
                start_angle = start_pos.heading
                target_angle = (start_angle + target_rotation) % 360
                # print(f"---Start angle is: {start_angle}, target angle is: {target_angle}")
                # Do the rotation
                pos = await set_wheel_speeds_dur(-current_wheel_speed,
                                                 current_wheel_speed,
                                                 target_rotation_dur)
                new_angle = pos.heading
                actual_rotation = new_angle - start_angle
                abs_diff = abs(actual_rotation - target_rotation)
                # print(f"---Abs diff (target - new): {abs_diff}")
                ratio = actual_rotation / target_rotation
                # print(f"---Ratio is: {ratio}")
                info(f"---Started at {start_angle}, wanted to end up at {target_angle}, ended up at {new_angle}.")
                info(f"---Wanted to rotate {target_rotation} degrees, travelled {actual_rotation} degrees instead.")
                info(f"---Difference: {target_rotation - actual_rotation}, ratio {ratio}")
                if abs_diff <= 2:
                    info(f"----abs difference close enough, setting speed from initial {init_wheel_speed} to final {current_wheel_speed}.")
                    speeds_dict[angular_speed] = current_wheel_speed
                    break
                else:
                    temp = current_wheel_speed / ratio
                    info(f"----adjusting speed from {current_wheel_speed} to {temp}.")
                    current_wheel_speed = temp
                    i += 1

    info("Callibration finished, here are the final wheel speeds:")
    info(speeds_dict)
    write_rotation_callibration_dict(speeds_dict)
