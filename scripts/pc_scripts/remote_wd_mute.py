import argparse

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
    _parser = argparse.ArgumentParser(prog="remote-WD-mute", description="Mute remote's WD.")
    _parser.add_argument("hostname", type=str, help="Remote's hostname/IP.")
    _parser.add_argument("username", type=str, help="Remote's username.")
    _parser.add_argument("password", type=str, help="Remote's password.")

    def run(self):
        """Main logic of the script that inherits the SSH script."""
        print(f'Running "{WD_STFU}" on remote')
        _, stdout, stderr = self._ssh_client.exec_command(WD_STFU)


if __name__ == "__main__":
    RemoteWDMute.new().run()
