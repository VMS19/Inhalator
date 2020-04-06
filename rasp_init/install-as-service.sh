#!/usr/bin/env bash

# fail on first error
set -e

curdir=$(dirname $0)
echo "We are at $curdir"
echo "generating service file..."
$(which python3) $curdir/create-service-file.py -o $curdir/inhalator.service

echo "installing the service file..."
sudo install $curdir/inhalator.service /usr/lib/systemd/user
echo "done!"

echo "enabling the service..."
sudo systemctl enable /usr/lib/systemd/user/inhalator.service
echo "done!"

echo "enabling pigpiod"
sudo systemctl enable pigpiod
echo "done!"

echo "disable NTP time, use time from RTC"
sudo timedatectl set-local-rtc true
sudo timedatectl set-ntp false
sudo timedatectl show
echo "done!"

echo "removing annoying ssh prompt"
sudo rm -f /etc/profile.d/sshpwd.sh /etc/profile.d/sshpasswd.sh /etc/xdg/lxsession/LXDE-pi/sshpwd.sh
echo "done!"

echo "reloading daemons (notifying systemd of a change)"
sudo systemctl daemon-reload
echo "done!"

sudo echo "starting the service"
systemctl start inhalator
