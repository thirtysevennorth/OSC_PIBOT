# OVERVIEW
This repo houses a framework for interacting with and controlling iCreate3 robots using OSC or Open Sound Control. It also has a bridge between OSC and ROS2. 

The OSC PIBOT framework goals are to provide a OSC based interface that allows for artist-friendly improvisational and performative control of a variety of robots, LEDs, motors and I2C devices from existing media and performance software tools like Max-MSP, Isadora, TouchDesigner, Qlab, and any other OSC capable software.

For each robot, a compute board such as a Raspberry Pi 4B, installed with Ubuntu 22.04, is running a Python script that sets up an OSC server, acting as a bridge between all other OSC clients and the iCreate3 itself (which can't receive OSC natively). Each Pi only listens for messages relating to its assigned robot, filters them, expands them to lower-level commands, and sends them directly to the robot via Bluetooth. For more reliable Bluetooth connection with longer range coverage, the Pis are mounted on the robots and receive OSC messages via a local WiFi network. An optional 'hub' computer may be employed to coordinate multiple robots.

Sample MAX-MSP and Isadora patches for use with the PIBOT framework are on the [**EXAMPLES**](docs/Examples.md) page. OSC PIBOT can be used with any OSC sender / receiver and additional sample files are welcomed. 

Two modes:
1) peer to peer - nodes run on the Pi on each robot and each directly receive/ transmit OSC messages 
2) one client, multiple servers - a machine running a robot sequencer (written in Clojure) can receive cue sheets with various behavioral routines placed on a timeline and coordinate the bots accordingly.

## ROS2
An experimental (and currently incomplete) ROS2 backend exists under `src/osc_bridge`. Its development was temporarily halted in favor of the Bluetooth-based [iRobot EDU Python SDK](https://github.com/iRobotEducation/irobot-edu-python-sdk), which appeared to have much better latency of command execution. We hope for future development to include additional ROS2 research, and welcome contributions.

## LED, POWER and AUDIO CONTROL
The framework provides unified OSC based control of supplemental I2C components controlled via the Pi. The customised boards developed provide 16 channels of I2C PWM based control of 12/24v LED lighting arrays as well as servo motor control, I2S audio outputs / input via an [Adafruit MAX98357 I2S amplifier](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp), and charge control for a supplemental USB 3 PD battery bank to deliver 12 and 15v power. The board is sized to fit in the iCreate drawer alongside a raspberry pi. 
 * A schematic file of the board we developed is [available here](docs/LED_PWM_driver_schematic.pdf). Please contact us if you would like information for a buildable copy of the board.
 * I2S software support is in process.


# INSTALLATION
The OSC PIBOT framework is intended for use on a raspberry Pi 4 or later running Ubuntu 22.04, and to communicate with an iCreate 3 or iCreate Root robot on the same local network as the Pi and OSC sender. 

## PI SETUP FOR PIBOT
The Pi should be setup running Ubuntu 22.04 with ports to send / receive UDP messages open. Bluetooth, I2C, I2S functionality must be enabled. 
 * Some pi's may require adjustments to the bluetooth settings to connect to the iCreate3 Bluetooth. See links for the specific build of Ubuntu 22.04 if you have issues. 
 * See the [**detailed set-up guide**](docs/Pi_CONFIGURATION.md) for additional guidance on configuring a Pi for use with the ICreate 3, the PIBOT script and ROS2. It documents our configuration of an Ubuntu 22.04.03 image. Your hardware and specific Ubuntu or Raspbian build may require adjustments.
 * Bluettoth pairing: On occasion some Pi devices experienced bluetooth pairing and connection issues to the iCreate3. There are a wide range of guides to troubleshoot bluetooth connection and pairign issues. We have found that delaying the start of the bluetooth service may help, as does cycling bluetooth on/off from the command line.

## Network configuration, Pihub and multiple robots
The hub/sequencer allows for control of multiple robots and multiple pi's from a unified OSC interface. 
 - You must configure the iCreate ROS namespace and device name to have unique names for each bot in the system.
 - See the [Network Diagram](docs/OSC_PIBOT_SIMPLE.png) for single bot or the [examples page](docs/Examples.md) for more detailed instructions.
 - you may need to adjust the UFW or other firewall settings of your local router and the individual pi's to allow for peer to peer UDP transmission. 


# EXAMPLES AND RESOURCES
Please see the [**EXAMPLES page**](docs/Examples.md) in the docs folder for example files, downloads and additional configuration resources.

# USAGE

## PIBOT 
The Pibot script will expect to find the following environment variables: 
- `MY_IP` - the script host's local IP address
- `MY_ID` - the assigned bot's ID, an integer number
- `MY_ROBOT_NAME` - the assigned robot's Bluetooth device name
- `PIHUB_OSC_IP` & `PIHUB_OSC_PORT` - IP address and port for OSC communications to the Pihub
- `ISADORA_OSC_IP` & `ISADORA_OSC_PORT` - IP address and port for OSC communications to the Pihub

Note: If there are no hub clients (i.e. Pihub & Isadora) then the environment variables can be placeholder IPs and ports.

Environment variables should be set up by editing and then running the `scripts/env.sh` [script](scripts/env.sh), or passed in directly at the shell. 

### START OSC PIBOT ON PI
Once installation and configuration is complete, from the Pi command line enter
```
    cd OSC_PIBOT/scripts 
    source ./env.sh
    source ./pibot-start
```
You should begin seeing status messages display on the pi terminal window.

To confirm communication try sending a OSC message such as `/pibot/command/play-note` from an OSC source. The robot should respond, and you should also see status messages display confirming. You can also watch the incoming OSC address & port you set for the update streams below such as `/pibot/update/battery`.

## START PIHUB (OPTIONAL)
On the PIHUB Pi, 
```
    cd OSC_PIBOT/scripts 
    source ./env.sh
    source ./pihub-start
```

## OSC MESSAGES
The following are a list of OSC messages in use along with their arguments and targets. Messages may be generated or received by any OSC source. 
[Examples.md](docs/Examples.md) has links to example file implementing these messages for a variety of software platforms, and [pibot_osc.py](src/pibot/pibot_osc.py) implements handlers for the messages.


### Update streams
- `/pibot/update/battery` -> int (bot ID), int (0 to 100)
  - sender(s): Pibots
  - receiver(s): Hub, Isadora
- `/pibot/update/position` -> int (bot ID), float (x), float (y) - (can be normalised)
  - sender(s): Pibots
  - receiver(s): Hub, Isadora
- `/pibot/update/is-docked` -> int (bot ID), bool
  - sender(s): Pibots
  - receiver(s): Hub, Isadora
- `/pibot/update/going-to-charge` -> int (bot ID)
  - sender(s): Pibots
  - receiver(s): Hub, Isadora
- `/pibot/update/charging` -> int (bot ID)
  - sender(s): Pibots
  - receiver(s): Hub, Isadora
- `/pibot/update/done-charging` -> int (bot ID)
  - sender(s): Pibots
  - receiver(s): Hub, Isadora

### Commands
- `/pibot/command/stop` -> bool
  - sender(s): Isadora
  - receiver(s): Hub (-> Pibots)
- `/pibot/command/play-note` -> int 
  - sender(s): Max Patch, Isadora
  - receiver(s): Hub (-> Pibots)
- `/pibot/command/go-to-point` -> int (robot ID), int
  - sender(s): Isadora
  - receiver(s): Hub (-> Pibots)
- `/pibot/command/set-LED`  -> rgbw (0..255) (Pi #, R, G, B, W, R2, G2, B2, W2) (expandable to 16 channels)
  - sender(s): Isadora
  - receiver(s): Hub (-> Pibots)
 
### direct to pi commands
- `/pibot/command/undock` -> (port, IP, Robot ID)
   - sender(s): Isadora / Max
   - Receiver: Pibots
- `/pibot/command/dock` -> (port, IP, Robot ID)
   - sender(s): Isadora / Max
   - Receiver: Pibots
- `/pibot/command/rotate` -> (port, IP, degrees, degrees per second, robot ID)
   - sender(s): Isadora / Max
   - Receiver: Pibots
- `/pibot/command/move` -> (port, IP, robot ID, Distance, Speed)
   - sender(s): Isadora / Max
   - Receiver: Pibots
- `/pibot/command/navigate-to` -> (port, IP, robot ID, x location, y location, Speed)
   - sender(s): Isadora / Max
   - Receiver: Pibots
- `/pibot/command/callibrate-rotation` -> (port, IP, robot ID)
   - sender(s): Isadora / Max
   - Receiver: Pibots

### direct to hub commands
- `/pihub/reload-cues` -> (hub port, hub IP)
   - sender(s): Isadora / Max
   - Receiver: Pibots
- `/pihub/set-scene` -> (hub port, hub IP, scene #)
   - sender(s): Isadora / Max
   - Receiver: Pibots


## ATTRIBUTION AND CREDITS

### x
The OSC PIBOT framework was originally developed for the **Dream Club Lab**,** a light and media art installation by [**Ian Winters**](https://ianwinters.com) and [**Elaine Buckholtz**](https://elainebuckholtz.format.com/), as a **Nighthouse Studios collaboration**, with a music score by [**Evelyn Ficarra**](https://evelynficarra.net, and robot programming Dimitris Kyriakoudis. Dream Club Lab was commissioned by the San Jose Downtown Association through the support of the City of San Jose and the Knight Foundation, with production support by [37 North](https://github.com/thirtysevennorth). Learn more about the [Dream Club Lab](https://dreamclublab.art) project.

### CONTRIBUTORS
Coding for OSC_PIBOT framework by[ Dimitris Kyriakoudis](https://github.com/monkey-w1n5t0n) with Ian Winters.
Hardware and framework concept by [Ian Winters](https://ianwinters.com).

Further development of the OSC PIBOT framework takes place through the AI Perform Initiatve at the University of Sussex led by [Professor Evelyn Ficarra](https://profiles.sussex.ac.uk/p41192-evelyn-ficarra), through 37 North and the Milkbar.
The Dream Club Lab will also be a course at Mass College of Art by Professor Elaine Buckholtz.

### CONTRIBUTIONS
Additional contributions to the development of artist oriented robotics software are welcomed as well as workshop inquiries.  

### LICENSE
The OSB PIBOT framework is released under the BSD 3-Clause License with no warranty of any kind. It uses the following open source direct dependencies, with license terms incorporated by reference, as well as those of any sub-dependencies. 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.

 - **[iRobot-edu-python sdk](https://github.com/iRobotEducation/irobot-edu-python-sdk)** licensed uder the BSD 3-Clause License, [available here](https://github.com/iRobotEducation/irobot-edu-python-sdk/blob/main/LICENSE.txt)
 - **[Bleak](https://github.com/hbldh/bleak)**, licensed under the MIT license, [available here](https://github.com/hbldh/bleak/blob/develop/LICENSE)
 - **[pySerial](https://github.com/pyserial/pyserial/)**, licensed under the BSD 3-Clause license, available here
 - **Root Robot Python Web App**, licensed under the MIT license, [available here](https://github.com/mogenson/root-robot-python-web-app/blob/main/LICENSE)
 - **[python-osc](https://pypi.org/project/python-osc/)**, Public Domain
 - **[Python 3](https://www.python.org/)**, under the [Python Software Foundation license](https://docs.python.org/3/license.html#psf-license)
 - **[Adafruit blinka and adafruit pca9685](https://github.com/adafruit/Adafruit_Blinka)** libraries licensed under the MIT license,
  [available here](https://github.com/adafruit/Adafruit_Blinka/blob/main/LICENSE)
 - **rclpy** licensed under the Apache 2 license [availble here](https://github.com/ros2/rclpy/blob/rolling/LICENSE)
 - **[ROS2 libraries](https://github.com/ros2)** from the [BSD 3-Clause license](https://docs.ros.org/en/diamondback/api/licenses.html)
 - **[Clojure](https://github.com/clojure/clojure)**, licensed under an [EPL 1.0 license](https://opensource.org/license/epl-1-0)
 - **[Leiningen](https://codeberg.org/leiningen/leiningen)**, licensed under an [EPL 1.0 license](https://opensource.org/license/epl-1-0)

