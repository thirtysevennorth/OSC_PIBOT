#!/usr/bin/env sh

# export MY_ID="1"
# export MY_ROBOT_NAME="iRobotCreate3"

# Check if the first argument is -env and if ./env/bin/python3 exists
if [ "$1" = "--venv" ] && [ -f "./env/bin/python3" ]; then
    # Use the python interpreter from the local venv
    ./env/bin/python3 main.py
else
    # Use the default python interpreter
    python3 main.py
fi


# #!/usr/bin/env sh

# export MY_ID="1"
# export MY_ROBOT_NAME="iRobotCreate3"
# export PIHUB_OSC_IP="192.168.1.212"
# export PIHUB_OSC_PORT="1338"
# export MY_IP="192.168.1.212"
# export PIBOT_OSC_PORT="1338"
# python3 main.py
