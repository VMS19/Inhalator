#!/bin/sh

unzip -p 2020-02-13-raspbian-buster.zip
sudo dd bs=4M if=2020-02-13-raspbian-buster.img of=/dev/mmcblk0 status=progress conv=fsync

#should sha256 the sdcard
sync