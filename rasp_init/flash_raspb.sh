#!/bin/sh

sudo dd bs=4M if=raspbian_operational.img of=/dev/mmcblk0 status=progress conv=fsync
sudo dd bs=4M of=/dev/mmcblk0 if=raspbian_operational_dump.img status=progress conv=fsync coun=1800
truncate --reference raspbian_operational.img raspbian_operational_dump.img
diff -s raspbian_operational.img raspbian_operational_dump.img
sync