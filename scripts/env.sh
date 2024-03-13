#!/usr/bin/env sh

export PIHUB_OSC_IP="192.168.0.103" # your IP HERE
export PIBOT_1_OSC_IP="192.168.0.101" # your IP HERE
export PIBOT_2_OSC_IP="192.168.0.102" # your IP HERE

export PIHUB_OSC_PORT="1337"
export PIBOT_OSC_PORT="1338"

# SCRIPT_DIR="$(dirname "$(realpath "$0")")"
# SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_DIR="$(cd "$(dirname -- "$0")" && pwd)"
export PIBOT_SCRIPT_DIR="$SCRIPT_DIR"

export PIBOT_HOME="$SCRIPT_DIR/../src/pibot"
export PIHUB_HOME="$SCRIPT_DIR/../src/pihub/sequencer"

export ISADORA_OSC_IP="192.168.0.200" # your IP HERE
export ISADORA_OSC_PORT="1234"

echo "Env script sourced."
