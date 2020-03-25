# Breathing Air

Turning stupid BiPAP into full-scale inhalators. 

## Getting Started
Make sure to install all of the project's dependencies
```shell script
pip3 install -r requirements.txt
```

Configure your `Raspberry Pi` using the the shell scripts found under the `rasp_init` directory.

Make sure you are running `Python 3.6+`, then simply run it using
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
