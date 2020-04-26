#!/bin/bash

# append a line to a file only if it doesn't already exist.
# parameters: line to append, file to append to
function idempotent_append {
	grep -xqF "$1" "$2" || echo -e "$1" >> "$2"
}

# exit if not running on a rpi
uname -a | grep -q raspberrypi && RPI="1"
if [ -z $RPI ]
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

# check if this is running as an installation or as an update
grep -q "exit 0 #remove this" /etc/rc.local && SETUP="1"


INHALATOR_PATH=$(realpath $(dirname $(realpath $0))/..)

if [ $SETUP ]
then
	echo "Installing dependencies"
	apt-get update
	apt install --assume-yes virtualenv libatlas-base-dev pigpio python3-dev vim
	apt-get install proftpd -y
	echo "Creating virtual env"
	virtualenv $INHALATOR_PATH/.inhalator_env -p $(which python3)
	source $INHALATOR_PATH/.inhalator_env/bin/activate
	pip3 install --upgrade pip
	pip3 install -r $INHALATOR_PATH/requirements.txt
fi

# install as service
$INHALATOR_PATH/rasp_init/install-as-service.sh

# enable ftp server
idempotent_append "UseReverseDNS off" /etc/proftpd/proftpd.conf
service proftpd restart

# enable ssh
systemctl enable ssh
systemctl start ssh

# configure network
echo "Setting up network"
grep -qF "192.168.1.253" /etc/network/interfaces || echo -e \
	"auto eth0\niface eth0 inet static\naddress 192.168.1.253/24\nnetmask 255.255.255.0" \
	>> /etc/network/interfaces

echo "Setting up graphics"
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
echo "Disabling bluetooth"
idempotent_append "dtoverlay=disable-bt" /boot/config.txt

# set keyboard layout
if [ $LANG != "en_US.UTF-8" ]
then
	echo "Setting locale"
	raspi-config nonint do_change_locale en_US.UTF-8
	raspi-config nonint do_configure_keyboard us
fi

echo "Enabling I2C and SPI"
# enable I2C
sudo raspi-config nonint do_i2c 0

# enable SPI
sudo raspi-config nonint do_spi 0

# set timezone
echo "Setting timezone"
[ $(date +"%Z") == "IDT" ] || timedatectl set-timezone 'Asia/Jerusalem'

# add the interpreter from the venv to PATH
idempotent_append "source /home/pi/Inhalator/.inhalator_env/bin/activate" /home/pi/.bashrc

# add ll and lla to bashrc
idempotent_append "alias ll='ls -l'" /home/pi/.bashrc
idempotent_append "alias lla='ls -la'" /home/pi/.bashrc

# re-enable file system expansion
echo "Disabling FS expansion"
sed -i 's/#init_here/init=\/usr\/lib\/raspi-config\/init_resize.sh/g' /boot/cmdline.txt
sed -i 's/exit 0 #remove this//g' /etc/rc.local
sed -i 's/8700000 #//g' /usr/lib/raspi-config/init_resize.sh

# config buzzer io pull up
echo "Pulling up GPIO-13"
idempotent_append "gpio=13=pu" /boot/config.txt

# enable hdmi hotplug
echo "Enabling HDMI hotplug"
idempotent_append "hdmi_force_hotplug=1" /boot/config.txt

echo "Enabling USB upgrade"
# disable the default automounting
sed -i 's/mount_on_startup=1/mount_on_startup=0/g' /etc/xdg/pcmanfm/LXDE-pi/pcmanfm.conf
sed -i 's/mount_removable=1/mount_removable=0/g' /etc/xdg/pcmanfm/LXDE-pi/pcmanfm.conf

# add a udev rule to catch the insertion of the DOK
if [ ! -f /etc/udev/rules.d/90-usbupgrade.rules ]
then
	echo 'KERNEL=="sd[a-z][0-9]", SUBSYSTEMS=="usb", ACTION=="add", RUN+="/bin/systemctl start usb-mount@%k.service"' > /etc/udev/rules.d/90-usbupgrade.rules
fi

# install the mounting service
[ -f /etc/systemd/system/usb-mount@.service ] || install $INHALATOR_PATH/rasp_init/usb-mount /etc/systemd/system/usb-mount@.service

# create mounting directory
mkdir -p /mnt/dok

# copy service script
[ -f /home/pi/mount_usb.sh ] || cp $INHALATOR_PATH/rasp_init/mount_usb.sh /home/pi/mount_usb.sh
chmod 777 /home/pi/mount_usb.sh

# set log rotation
sed -i 's/rotate .*/rotate 2/g' /etc/logrotate.d/rsyslog
sed -i 's/weekly/daily/g' /etc/logrotate.d/rsyslog
sed -i '/daily/a \\tsize 100m' /etc/logrotate.d/rsyslog

if [ $SETUP ]
then
	echo -e "setup done. DON'T FORGET TO CHANGE THE PASSWORD\nDO NOT REBOOT - USE ONLY SHUTDOWN!!!"
fi
