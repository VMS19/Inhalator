import consts
from script_classes.remote_ssh_script import RemoteSSHScript

WD_STFU = f"PYTHONPATH={consts.INHALATOR_REPO_FOLDER_PATH} python3 {consts.INHALATOR_REPO_FOLDER_PATH}/{consts.RPI_SCRIPTS_FOLDER}/wd_stfu.py &"


def print_stream_lines(stream_name, stream):
    lines = stream.readlines()

    if len(lines):
        print(f"+---{stream_name}---:")

    for line in lines:
        print(line)

    if len(lines):
        print(f"+-------------")


class RemoteWDMute(RemoteSSHScript):
    def __init__(self, init=False, parser_args=None):
        super(RemoteWDMute, self).__init__(init=init, parser_args=parser_args)
        self._parser.prog = "remote-WD-mute"
        self._parser.description = "Mute remote's WD."

    def _main(self):
        """Main logic of the script that inherits the SSH script."""
        print(f'Running "{WD_STFU}" on remote')
        _, stdout, stderr = self._ssh_client.exec_command(WD_STFU)


if __name__ == "__main__":
    RemoteWDMute.new().run()
