#!/bin/bash

# exit if not running on a rpi
uname -a | grep -q raspberrypi && RPI="1"
if [ -z $RPI ];
then
	echo "This script should only be run on a raspberrypi!"
	exit 1
fi

# exit if not running as root
if [ "root" != $(whoami) ]
then
	echo "This script should be run as root!"
	exit 1
fi

INHALATOR_PATH=$(realpath $(dirname $(realpath $0))/..)

# install dependencies
apt-get update
apt-get install --assume-yes virtualenv libatlas-base-dev pigpio python3-dev vim
virtualenv $INHALATOR_PATH/.inhalator_env -p $(which python3)
source $INHALATOR_PATH/.inhalator_env/bin/activate
pip3 install --upgrade pip
pip3 install -r $INHALATOR_PATH/requirements.txt

# enable ftp server
apt-get install proftpd -y
echo "UseReverseDNS off" >> /etc/proftpd/proftpd.conf
service proftpd restart

# install as service
$INHALATOR_PATH/rasp_init/install-as-service.sh

# enable ssh
systemctl enable ssh
systemctl start ssh

# configure network
echo -e "auto eth0\niface eth0 inet static\naddress 192.168.1.253/24\nnetmask 255.255.255.0" >> /etc/network/interfaces

# set the wallpaper
cp $INHALATOR_PATH/resources/wallpaper.png /usr/share/rpd-wallpaper/temple.jpg

# set boot screen
cp $INHALATOR_PATH/resources/wallpaper.png /usr/share/plymouth/themes/pix/splash.png

# disable screen saver
raspi-config nonint do_blanking 1

# remove trash icon from desktop
sed -i 's/show_trash=1/show_trash=0/g' /etc/xdg/pcmanfm/LXDE-pi/desktop-items-0.conf

# remove taskbar
sed -i 's/@lxpanel --profile LXDE-pi//g' /etc/xdg/lxsession/LXDE-pi/autostart

# remove mouse cursor
sed -i 's/#xserver-command=X/xserver-command=X -nocursor/g' /etc/lightdm/lightdm.conf

# disable first use wizard
rm -f /etc/xdg/autostart/piwiz.desktop

# disable BT
echo "dtoverlay=disable-bt" >> /boot/config.txt

# set keyboard layout
raspi-config nonint do_change_locale en_US.UTF-8
raspi-config nonint do_configure_keyboard us

# enable I2C
sudo raspi-config nonint do_i2c 0

# enable SPI
sudo raspi-config nonint do_spi 0

# set timezone
timedatectl set-timezone 'Asia/Jerusalem'

# add the interpreter from the venv to PATH
echo "source /home/pi/Inhalator/.inhalator_env/bin/activate" >> /home/pi/.bashrc

# add ll and lla to bashrc
echo -e "alias ll='ls -l'\nalias lla='ls -la'" >> /home/pi/.bashrc

# re-enable file system expansion
sed -i 's/#init_here/init=\/usr\/lib\/raspi-config\/init_resize.sh/g' /boot/cmdline.txt
sed -i 's/exit 0 #remove this//g' /etc/rc.local
sed -i 's/8700000 #//g' /usr/lib/raspi-config/init_resize.sh

# config buzzer io pull up
echo "gpio=13=pu" >> /boot/config.txt

# enable ftp server permissions to log files
touch /home/pi/Inhalator/inhalator.log
touch /home/pi/Inhalator/inhalator.csv
chown pi:pi /home/pi/Inhalator/inhaltor.*
chmod 777 /home/pi/Inhalator/inhalator.*

# enable hdmi hotplug
echo "hdmi_force_hotplug=1" >> /boot/config.txt

echo -e "setup done. DON'T FORGET TO CHANGE THE PASSWORD\nDO NOT REBOOT - USE ONLY SHUTDOWN!!!"
