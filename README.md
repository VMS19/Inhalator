# Medical ventilator monitor
![](https://github.com/Reznic/Inhalator/workflows/build/badge.svg) 
[![Coverage Status](https://coveralls.io/repos/github/Reznic/Inhalator/badge.svg?branch=master)](https://coveralls.io/github/Reznic/Inhalator?branch=master)


Monitoring for medical ventilation systems

## Getting Started
Make sure to install all of the project's dependencies
```shell script
pip3 install -r requirements.txt
```

Configure your `Raspberry Pi` using the the shell scripts found under the `rasp_init` directory.

Make sure you are running `Python 3.7+`, then simply run it using
```shell script
python3 main.py
```

## Inhalator as a SystemD Service

You should configure this program to run as a service on your Debian/Ubuntu/Raspbian machine:

(Make sure NOT to run this as root, it will prompt you for your root password whenever it's needed)
```shell script
rasp_init/install-as-service.sh
```
Then you can control the program using
```shell_script
sudo service inhalator start
```

and stop it by 
```shell_script
sudo service inhalator stop
```

## Running tests
You can run your tests using
```shell_script
tox
```
