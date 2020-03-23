#!/bin/bash

#enable wifi
sudo cat wpa_supplicant.conf >> /etc/wpa_supplicant/wpa_supplicant.conf
sudo rfkill unblock wifi
sudo wpa_passphrase "" "" >> /etc/wpa_supplicant/wpa_supplicant.conf
sudo wpa_cli reconfigure

#enable ssh
sudo systemctl enable ssh
sudo systemctl start ssh