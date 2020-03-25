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

sudo echo "starting the service"
systemctl start inhalator