#!/bin/bash

VERSION=$(basename /mnt/dok/inhalator*.tar.gz | cut -d"." -f 1)

if [[ -d /home/pi/$VERSION ]]; then
	echo "Inhalator version is updated"
	sleep 3
	exit 0
fi

echo -n "Copying new files.."
echo " -C /home/pi/ --transform s/Inhalator/$VERSION/" | xargs tar xf /home/pi/inhalator*.tar.gz

echo -n "Replacing inhalator service..."
sudo cp /usr/lib/systemd/user/inhalator.service setup.tmp
sudo bash -c "sed 's/Inhalator/${VERSION}/' setup.tmp > /usr/lib/systemd/user/inhalator.service"

echo -n "Moving the config.json file..."
sudo cp /home/pi/Inhalator/config.json /home/pi/$VERSION/config.json

echo -n "Deleting old files... "
sudo rm -rf $(readlink /home/pi/Inhalator) 1> /dev/null
sudo rm -rf /home/pi/Inhalator 1> /dev/null
echo "Done."

echo -n "stopping Inhalator service... "
sudo systemctl stop inhalator.service 1> /dev/null
echo "Done."

echo -n "Linking new version..."
sudo ln -s /home/pi/$VERSION /home/pi/Inhalator

echo -n "Fixing inhalator service..."
sudo mv setup.tmp /usr/lib/systemd/user/inhalator.service

echo -n "Running setup script... "
sudo /home/pi/Inhalator/rasp_init/setup.sh 1> /dev/null
echo "Done."
echo -n "Restarting service... "
sudo systemctl start inhalator.service 1> /dev/null
echo "Done."
sleep 2
