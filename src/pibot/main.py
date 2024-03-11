#!/usr/bin/env python3
#
# This software provided under the BSD 3-Clause License
# Copyright (c) 2024, 37 North, Inc.
# Primary contributors Dimitris Kyiakoudis and Ian Winters.
# Additional libraries used subject to the licenses listed in README.MD
# at https://https://github.com/thirtysevennorth/OSC_PIBOT.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#  contributors may be used to endorse or promote products derived from
#  this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

from pibot_utils import *
import pibot_utils
from pibot_commands import *
from pibot_osc import *
import pibot_status
import asyncio
import math
import time
import os
import sys

info("Script started.")
main_log("APP", "Script started.")

setup_i2c()

battery = 90 # hack to fix low battery level
update_status_sleep_dur = 0.33

def notify_servers_and_quit():
    main_log("APP", "Quitting.")
    message_servers("/pibot/update/reconnecting", [int(my_id)])
    global server_transport
    server_transport.close()
    sys.exit(1)

async def go_to_charge():
    info("Going to charge.")
    main_log("CHARGE", "Going to charge.")
    message_servers("/pibot/update/going-to-charge", [int(my_id)])
    pibot_status.busy_charging = True
    await dock_after_this()
    message_servers("/pibot/update/charging", [int(my_id)])

@event(robot.when_play)
async def update_status(robot):
    try:
        while True:
            battery = await get_battery()
            # debug(f"Battery: {battery}")
            pos = await get_pos()
            # debug(f"Pos: {pos}")
            contacts = await check_docking_contacts()
            # debug(f"Contacts: {contacts}")
            pibot_status.is_docked = contacts

            # don't do anything if either request didn't succeed
            if not battery or not pos:
                error("Received 'None' when asking robot for battery and position, which probably means that the Bluetooth connection isn't working. Waiting to see if exception is raised...")
                debug(f"==> Battery: {battery}, Position: {pos}")
                # await asyncio.sleep(update_status_sleep_dur)
                notify_servers_and_quit()
                # continue

            percentage = battery[1]

            # Update servers with battery & pos
            message_servers("/pibot/update/battery", [int(my_id), int(percentage)])
            message_servers("/pibot/update/position", [int(my_id), pos.x, pos.y, pos.heading])
            message_servers("/pibot/update/is-docked", [int(my_id), pibot_status.is_docked])

            # Charge if battery is low
            if not pibot_status.busy_charging and not pibot_status.is_docked and percentage < min_battery:
                info(f"Battery is low ({percentage}%), under {min_battery}%")
                await go_to_charge()
            # Notify servers and start listening when battery has recharged
            elif pibot_status.busy_charging and pibot_status.is_docked and percentage >= max_battery:
                pibot_status.busy_charging = False
                message_servers("/pibot/update/done-charging", [int(my_id)])
    except Exception as e:
        error(f"Exception occurred inside 'update_status':/n{e}/n==> Exiting with error code 1...")
        notify_servers_and_quit()

@event(robot.when_play)
async def continuously_execute_command_q(robot):
    while True:
        # Process each coroutine in the queue until it's empty
        await pibot_utils.command_q_lock.acquire()  # Acquire the lock before executing the command
        while True:
            if pibot_utils.command_q.empty():
                break
            command = pibot_utils.command_q.get()
            await command
        pibot_utils.command_q_lock.release()  # Release the lock after the command is executed
        # wait a little before checking the queue again
        await asyncio.sleep(0.01)

@event(robot.when_play)
async def pibot_start(robot):
    info(f"Successfully connected to robot with name: {my_robot_name}.")
    await pibot_start_osc_server_listening()

robot.play()
