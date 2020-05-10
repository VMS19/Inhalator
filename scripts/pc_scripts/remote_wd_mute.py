from scripts.scripts_utils import consts
from scripts.scripts_utils.remote_ssh_script import RemoteSSHScript

WD_STFU = f"PYTHONPATH={consts.INHALATOR_REPO_FOLDER_PATH} python3 {consts.INHALATOR_REPO_FOLDER_PATH}/{consts.RPI_SCRIPTS_FOLDER}/mute_wd.py &"


def print_stream_lines(stream_name, stream):
    lines = stream.readlines()

    if len(lines):
        print(f"+---{stream_name}---:")

    for line in lines:
        print(line)

    if len(lines):
        print(f"+-------------")


class RemoteWDMute(RemoteSSHScript):
    def __init__(self):
        super(RemoteWDMute, self).__init__()
        self._parser.prog = "remote-WD-mute"
        self._parser.description = "Mute remote's WD."

    def _main(self, args, pre_run_variables):
        """Main logic of the script that inherits the SSH script."""
        print(f'Running "{WD_STFU}" on remote')
        ssh_client = pre_run_variables["ssh_client"]
        ssh_client.exec_command(WD_STFU)


if __name__ == "__main__":
    RemoteWDMute().run()
