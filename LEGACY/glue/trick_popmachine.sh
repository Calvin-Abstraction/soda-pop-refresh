#!/bin/bash
#
# Run the trick_popmachine daemon. Call this in an init script at boot.
#
# Author: John Kloosterman
# Date: Mar. 1, 2011

DEVICE="/dev/ttyUSB0"
POP_PATH="/home/pi/soda-pop-refresh/LEGACY"

$POP_PATH/trick_popmachine/trick_popmachine $DEVICE
