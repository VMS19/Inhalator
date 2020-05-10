import argparse
import os


SERVICE_PATH = "/usr/lib/systemd/user/inhalator.service"
SYSTEMD_SERVICE = """
[Unit]
Description=Inhalator Service

[Service]
ExecStart=/home/pi/Inhalator/.inhalator_env/bin/python3 /home/pi/Inhalator/main.py {}
WorkingDirectory=/home/pi/Inhalator
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/pi/.Xauthority
Restart=always
Type=simple

[Install]
WantedBy=default.target
"""


def main(is_debug):
    service_content = SYSTEMD_SERVICE.format("-d -vvv" if is_debug
                                             else "")

    with open(SERVICE_PATH, "w") as service_file:
        service_file.write(service_content)

    os.system("rm /home/pi/Inhalator/config.json")
    os.system("chmod 777 /home/pi/Inhalator/inhalator.*")
    os.system("""sed -i 's/"boot_alert_grace_time" : 5/"boot_alert_grace_time" : -5099766400/' /home/pi/Inhalator/default_config.json""")
    os.system("systemctl daemon-reload")
    os.system("systemctl restart inhalator")
    os.system("echo 'UseReverseDNS off' >> /etc/proftpd/proftpd.conf")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Change log mode to debug or back to production")
    parser.add_argument("--debug", action="store_true",
                        help="Whether to enable debug mode or not")
    args = parser.parse_args()

    main(args.debug)
