#!/bin/bash

# exit if not running on a rpi
uname -a | grep -q raspberrypi && RPI="1"
if [ -z $RPI ];
then
	echo "This script should only be run on a raspberrypi!"
	exit 1
fi

INHALATOR_PATH=$(realpath $(dirname $(realpath $0))/..)

# install dependencies
apt install --assume-yes virtualenv libatlas-base-dev
virtualenv $INHALATOR_PATH/.inhalator_env -p $(which python3)
source $INHALATOR_PATH/.inhalator_env/bin/activate
pip3 install --upgrade pip
pip3 install -r $INHALATOR_PATH/requirements.txt

# enable ssh
sudo systemctl enable ssh
sudo systemctl start ssh

# install as service
$INHALATOR_PATH/rasp_init/install-as-service.sh

# configure network
echo -e "dtoverlay=disable-wifi\ndtoverlay=disable-bt" >> /boot/config.txt
echo -e "interface eth0\nstatic ip_address=192.168.1.1/24" >> /etc/dhcpcd.conf

# set the wallpaper
cp $INHALATOR_PATH/resources/wallpaper.png /usr/share/rpd-wallpaper/temple.jpg

# set boot screen
cp $INHALATOR_PATH/resources/wallpaper.png /usr/share/plymouth/themes/pix/splash.png

# disable screen saver
raspi-config nonint do_blanking 1
