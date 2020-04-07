#!/bin/bash

# Set date on remote machine
sshpass -p 'raspberry' ssh pi@1.1.1.1 sudo date -s @`( date -u +"%s" )`

# Set rtc time
sshpass -p 'raspberry' ssh pi@1.1.1.1 '~/Inhalator/scripts/set_rtc_time.py'
