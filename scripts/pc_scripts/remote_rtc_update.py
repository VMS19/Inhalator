from datetime import datetime

from scripts.scripts_utils import consts
from scripts.scripts_utils.remote_ssh_script import RemoteSSHScript


UPDATE_RTC_TIME_CMD = f"PYTHONPATH={consts.INHALATOR_REPO_FOLDER_PATH} python3 {consts.INHALATOR_REPO_FOLDER_PATH}/{consts.RPI_SCRIPTS_FOLDER}/update_rtc_time.py"


def print_stream_lines(stream_name, stream):
    lines = stream.readlines()

    if len(lines):
        print(f"+---{stream_name}---:")

    for line in lines:
        print(line)

    if len(lines):
        print(f"+-------------")


class RemoteRTCUpdate(RemoteSSHScript):
    """Script that update the remote's rtc according to the current datetime via SSH."""
    def __init__(self):
        super(RemoteRTCUpdate, self).__init__()
        self._parser.prog = "remote-rtc-update"
        self._parser.description = "Update remote's RTC."

    def _main(self, args, pre_run_variables):
        """Update the remote's rtc according to the current datetime via SSH."""
        ssh_client = pre_run_variables["ssh_client"]
        current_datetime = datetime.now()

        _, stdout, stderr = ssh_client.exec_command("sudo date -s '{}' > /dev/null".format(current_datetime.isoformat()))
        print_stream_lines("stdout", stdout)
        print_stream_lines("stderr", stderr)

        _, stdout, stderr = ssh_client.exec_command(UPDATE_RTC_TIME_CMD)

        print_stream_lines("stdout", stdout)
        print_stream_lines("stderr", stderr)


if __name__ == "__main__":
    RemoteRTCUpdate().run()
