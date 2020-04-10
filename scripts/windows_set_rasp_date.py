import sys
import os
from datetime import datetime
try:
    import paramiko
    from paramiko import SSHClient
except ImportError:
    print("please 'pip install paramiko'!!!!")
    raise

sys.path.append(os.path.dirname('.'))


def main():
    cur_date = datetime.now()
    print('setting date: ', cur_date.isoformat())
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(sys.argv[1], username=sys.argv[2], password=sys.argv[3], look_for_keys=False)
    stdin, stdout, stderr = client.exec_command("sudo date -s '{}' > /dev/null".
                                                format(cur_date.isoformat()))
    stdin, stdout, stderr = client.exec_command("PYTHONPATH=~/Inhalator \
                                                 ~/Inhalator/.inhalator_env/bin/python\
                                                 ~/Inhalator/scripts/set_rtc_time.py")


if __name__ == "__main__":
    main()
