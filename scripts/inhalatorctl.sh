#!/bin/bash

IP=192.168.1.49
PASSWORD=raspberry


get_mac () {
	echo $(sshpass -p $PASSWORD ssh pi@$IP 'cat /sys/class/net/eth0/address')
}

set_time () {
	sshpass -p $PASSWORD ssh pi@$IP <<ENDSSH
	sudo su
	date -s $(date --iso-8601=seconds)
	PYTHONPATH=/home/pi/Inhalator /home/pi/Inhalator/.inhalator_env/bin/python3 /home/pi/Inhalator/scripts/set_rtc_time.py
ENDSSH
}

upgrade_version () {
	sshpass -p $PASSWORD scp ~/Desktop/inhalator.tar.gz pi@$IP:/home/pi/
	sshpass -p $PASSWORD ssh pi@$IP <<ENDSSH
	sudo su
	systemctl stop inhalator.service
	rm -rf /home/pi/Inhalator
	tar xzf /home/pi/inhalator.tar.gz
	rm /home/pi/inhalator.tar.gz
	systemctl start inhalator.service
ENDSSH
}

MAC=$(get_mac)
echo "MAC address: $MAC"

set_time
# upgrade_version


# (echo 12345678 ; echo raspberry ; echo raspberry) | passwd