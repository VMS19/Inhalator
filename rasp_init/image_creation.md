# Inhalator setup
To install The Inhalator app on a Raspberry pi, one must flash a valid image to an SD card. This file documents the creation of such an image.

## Requirements
 - A Linux computer with an SD card interface
 - A micro-SD card with a suitable adapter to your SD card interface
 - A Raspberry pi 3B+ with a monitor and keyboard
 - A router with an Ethernet cable

## Step 1: Flash a template image
The first step of creating an image is to flash a template image. The template image is used as a base for creating Inhalator images.
Templates could be found on the releases page. Download the template accompanying the version you want to install. If you can't find a template file, search in older releases, though make sure you use the most up to date version.  Flash the template to an SD card using dd:

    sudo dd bs=4M if=template-1-1-1.img of=/dev/mmcblk0 status=progress conv=fsync
**Warning!** The `of` argument defines the output file of dd. In this example it's set to `/dev/mmcblk0`, the device file of the SD card. Make sure you enter the correct device, as dd will overwrite anything on its target device. If you input the wrong device, you can lose data or terminally damage your computer. Use the `lsblk` command to find the correct device file.

## Step 2: Change the password
Insert the flashed SD card into a Raspberry pi. Turn it on, connect it to an Ethernet port (don't turn on WiFi!) and open up a terminal. Change the password using `passwd`. The default password is `raspberry`. Change it to the correct password used by your organization.

## Step 3: Clone and install the repository
Clone the repository by typing the following while the working directory is `/home/pi`:

    git clone https://github.com/VMS19/Inhalator.git
After the download is complete, install the app by typing:

    sudo Inhalator/rasp_init/setup.sh
This script will take a few minutes to run. When it's finished, turn off the Raspberry pi using:

    sudo shutdown now
**Do not reboot!** Use only shutdown. Reboot only after the image has been dumped.
## Step 4: Dump the SD card
The final step of creating an image is to extract the bytes on the SD card to an image file. After disconnecting the power supply, take the SD card out of the Raspberry pi and insert it to your computer. Use dd to dump the contents of the SD card:

    sudo dd count=8700000 if=/dev/mmcblk0 of=inhalator_x-x-x.img status=progress conv=fsync
Notice that the `if` argument defines the input file of the command, and should be set to the device file of the SD card. Usually it's called `/dev/mmcblk0`, but to make sure use the `lsblk` command.
When dd is done, you will have a valid image to flash to many ventilators!
You can use dd to flash the SD cards, or, on Windows, use an imaging app such as Win32DiskImager.
## Bonus: Creating an upgrade package
If you have an already working ventilator, you might want to update its software without taking out the SD card and re-flashing it. Luckily, the Inhalator app support software updates. Those updates require an upgrade package: a compressed file of the app. This package is extracted from another Raspberry pi. You can use the same setup used to create the image for creating the upgrade package.
After you've finished dumping the SD card, insert it back to the Raspberry pi. Turn it on and wait for the app to launch. Open up a terminal using `ctrl + alt + t`, and type the following:

    sudo systemctl stop inhalator.service
This will stop the app, so that we can compress it using this command:

    tar cvfz inhalator_x-x-x.tar.gz Inhalator/
This will take all the files in Inhalator and compress them to a file named `inhalator_x-x-x.tar.gz` (replace x-x-x with the version number). To retrieve the file from the Raspberry pi, there are two options:

 1. Connect to the pi via Ethernet (the IP address of the pi should now be `192.168.1.253`) and use `scp` to copy the file to your computer.
 2. Turn the Raspberry pi off, insert the SD card to your computer, mount the rootfs to your computer, and copy the file.

That's it! Upload the two files you created to the releases page and you're done!
