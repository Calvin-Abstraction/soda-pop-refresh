#!/bin/bash
#
# This should be run as a cron job to update the pop machine data.
#
# Author: John Kloosterman
# Date: Feb. 28, 2011

DEVICE="/dev/ttyUSB0"
POP_PATH="/home/john/popmachine"
DATE=`date +%F_%R`

echo "$DATE : Updating pop machine data..."

# 1: Stop the machine-fooling daemon
killall -SIGUSR1 trick_popmachine
sleep 1

# 2: Pull data from pop machine
$POP_PATH/dex_communicate/dex_communicate $DEVICE > /tmp/$DATE.dex
if [ $? == 1 ]; then
	echo "Communication with pop machine failed."

	# Re-enable machine-fooling daemon
	# It's super-important this is running all the time!
	$POP_PATH/trick_popmachine/trick_popmachine $DEVICE
	echo "Done updating pop machine data."
	exit 1
fi

# 3: Re-enable the machine-fooline daemon
$POP_PATH/trick_popmachine/trick_popmachine $DEVICE

# 4: Parse the raw data to XML
$POP_PATH/dex_parser/dex_parser -xml < /tmp/$DATE.dex > /tmp/$DATE.xml

# 5: Add the XML file to the database.
$POP_PATH/xmltodb/parsexml.py /tmp/$DATE.xml

# 6: Update Twitter!
$POP_PATH/web_interface/update_twitter.py

# 7: Clean up intermediate files.
rm /tmp/$DATE.dex
rm /tmp/$DATE.xml

echo "Done updating pop machine data."
