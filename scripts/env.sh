#!/usr/bin/env sh

export PIHUB_OSC_IP="192.168.0.31"
export PIBOT_1_OSC_IP="192.168.0.121"
export PIBOT_2_OSC_IP="192.168.0.120"

export PIHUB_OSC_PORT="1337"
export PIBOT_OSC_PORT="1338"

# SCRIPT_DIR="$(dirname "$(realpath "$0")")"
# SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT_DIR="$(cd "$(dirname -- "$0")" && pwd)"
export PIBOT_SCRIPT_DIR="$SCRIPT_DIR"

export PIBOT_HOME="$SCRIPT_DIR/../src/pibot"
export PIHUB_HOME="$SCRIPT_DIR/../src/pihub/sequencer"

export ISADORA_OSC_IP="192.168.1.223"
export ISADORA_OSC_PORT="1234"

echo "Env script sourced."
