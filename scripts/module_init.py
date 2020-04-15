import sys
import paramiko
import datetime

USAGE = "Usage: python3 module_init.py ip_address password"

if len(sys.argv) != 3:
	print(USAGE)
	exit()

hostname = sys.argv[1]
password = sys.argv[2]

username = "pi"
port = 22


RTC_COMMAND = "sudo date -s {}\n" \
"PYTHONPATH=/home/pi/Inhalator /home/pi/Inhalator/.inhalator_env/bin/python3 /home/pi/Inhalator/scripts/set_rtc_time.py"


try:
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy)
    
    client.connect(hostname, port=port, username=username, password=password)

    _, mac_stdout, _ = client.exec_command("cat /sys/class/net/eth0/address")
    _, rtc_stdout, _ = client.exec_command(RTC_COMMAND.format(datetime.datetime.now().isoformat()))
    print("Module MAC address:     ", mac_stdout.read().decode("ascii")[:-1])
    print("Module time (verify!):  ", rtc_stdout.read().decode("ascii")[:-1])

finally:
    client.close()