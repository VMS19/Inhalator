#!/bin/bash

export DISPLAY=":0"
export XAUTHORITY="/home/pi/.Xauthority"
DEV="/dev/$1"

sudo mount -t vfat $DEV /mnt/dok
sudo x-terminal-emulator -e "/mnt/dok/setup.sh && echo 'Completed successfully' || Failed; sleep 3"
sudo umount /mnt/dok
sudo systemctl stop usb-mount@sda1.service
