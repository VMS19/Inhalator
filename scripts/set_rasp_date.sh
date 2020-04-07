#!/bin/bash

IP_ADDR=$1
if [[ $# -eq 0 ]]; then
    echo "No ip supplied"
else
    # Set date on remote machine
    sshpass -p 'raspberry' ssh pi@$IP_ADDR sudo date -s @`( date -u +"%s" )`

    # Set rtc time
    sshpass -p 'raspberry' ssh pi@$IP_ADDR '~/Inhalator/scripts/set_rtc_time.py'
fi
