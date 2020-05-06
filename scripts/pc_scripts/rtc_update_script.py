import argparse
from datetime import datetime

import consts
from script_classes.remote_ssh_script import RemoteSSHScript


SET_RTC_TIME_CMD = "PYTHONPATH={consts.INHALATOR_REPO_FOLDER_PATH} python3 {consts.INHALATOR_REPO_FOLDER_PATH}/{consts.RPI_SCRIPTS_FOLDER}/set_rtc_time.py"


def print_stream_lines(stream_name, stream):
    lines = stream.readlines()

    if len(lines):
        print(f"+---{stream_name}---:")

    for line in lines:
        print(line)

    if len(lines):
        print(f"+-------------")


class RemoteRTCUpdate(RemoteSSHScript):
    _parser = argparse.ArgumentParser(prog="remote-RTC-update", description="Update remote's RTC..")
    _parser.add_argument("hostname", type=str, help="Remote's hostname/IP.")
    _parser.add_argument("username", type=str, help="Remote's username.")
    _parser.add_argument("password", type=str, help="Remote's password.")

    def run(self):
        """Main logic of the script that inherits the SSH script."""
        current_datetime = datetime.now()

        _, stdout, stderr = self._ssh_client.exec_command("sudo date -s '{}' > /dev/null".format(current_datetime.isoformat()))
        print_stream_lines("stdout", stdout)
        print_stream_lines("stderr", stderr)

        _, stdout, stderr = self._ssh_client.exec_command(SET_RTC_TIME_CMD)

        print_stream_lines("stdout", stdout)
        print_stream_lines("stderr", stderr)


if __name__ == "__main__":
    RemoteRTCUpdate.new().run()
