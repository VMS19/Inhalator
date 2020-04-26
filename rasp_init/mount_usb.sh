#!/bin/bash

export DISPLAY=":0"
export XAUTHORITY="/home/pi/.Xauthority"
DEV="/dev/$1"

sudo mount -t vfat $DEV /mnt/dok
if [ $? -ne  0 ]
then
	sudo x-terminal-emulator -e "echo 'Failed to mount device. Aborting' ; sleep 3"
else
	sudo x-terminal-emulator -e "/mnt/dok/setup.sh && echo 'Completed successfully' || echo 'Failed' ; sleep 3"
	sudo umount /mnt/dok
fi

sudo systemctl stop usb-mount@sda1.service
