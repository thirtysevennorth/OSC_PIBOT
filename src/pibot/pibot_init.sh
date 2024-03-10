#!/usr/bin/env sh

# Start Python server
init_py=$HOME/pibot/main.py

if [ -f $init_py ]; then
    python3 $init_py
else
    echo "Warning: $init_py does not exist."
fi
