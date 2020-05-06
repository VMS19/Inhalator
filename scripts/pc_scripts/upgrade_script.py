import ntpath
import argparse
from datetime import datetime

import consts
from script_classes.remote_scp_script import RemoteScpScript


REMOTE_TRANSFER_DEST_PATH = "/home/pi"
WD_STFU = f"PYTHONPATH={consts.INHALATOR_REPO_FOLDER_PATH} python3 {consts.INHALATOR_REPO_FOLDER_PATH}/{consts.RPI_SCRIPTS_FOLDER}/wd_stfu.py &"


def print_stream_lines(stream_name, stream):
    lines = stream.readlines()

    if len(lines):
        print(f"+---{stream_name}---:")

    for line in lines:
        print(line)

    if len(lines):
        print(f"+-------------")


class UpgradeScript(RemoteScpScript):
    _parser = argparse.ArgumentParser(prog="upgrade-script", description="Change the version on the remote inhalator monitor.")
    _parser.add_argument("hostname", type=str, help="Remote's hostname/IP.")
    _parser.add_argument("username", type=str, help="Remote's username.")
    _parser.add_argument("password", type=str, help="Remote's password.")
    _parser.add_argument("version_tarball_path", type=str, help="Local version's tarball file path.")
    _parser.add_argument("-d", "--debug", action="store_true")

    def run(self):
        """Main logic of the script that inherits the SSH script."""
        tarball_basename = ntpath.basename(self._args.version_tarball_path)
        # Muting the wd.
        self._ssh_client.exec_command(WD_STFU)
        print("Finished running the WD mute script.")
        # Transfering the version tarball.
        before_transfer_datetime = datetime.now()
        self._scp_client.put(self._args.version_tarball_path, "/home/pi/")
        after_transfer_datetime = datetime.now()
        print("Finished transfering the version's tarball.")
        # Running the script to stop the service, install the new version and start the service again.
        print("")

        UPGRADE_SCRIPT = [
            f"sudo systemctl stop {consts.INHALATOR_SERVICE_NAME}",
            f"sudo rm -rf {consts.INHALATOR_REPO_FOLDER_PATH}",
            f"tar xf {REMOTE_TRANSFER_DEST_PATH}/{tarball_basename} -C {consts.INHALATOR_REPO_FOLDER_PATH} --warning=no-timestamp",
            f"sudo rm -f {REMOTE_TRANSFER_DEST_PATH}/{tarball_basename}",
            f"sudo {consts.INHALATOR_REPO_FOLDER_PATH}/{consts.RPI_INIT_SCRIPTS_FOLDER}/setup.sh",
            f"sudo sync",
            f"sync",
            f"sleep 1",
            f"sudo systemctl start {consts.INHALATOR_SERVICE_NAME}",
        ]

        for cmd in UPGRADE_SCRIPT:
            cmd = cmd
            print(f"Running \"{cmd}\" on remote.")
            before_cmd_exec = datetime.now()
            _, stdout, stderr = self._ssh_client.exec_command(cmd)

            if self._args.debug:
                print_stream_lines("stdout", stdout)
                print_stream_lines("stderr", stderr)
            after_cmd_exec = datetime.now()
            print_cmd_exec_time = (after_cmd_exec - before_cmd_exec).total_seconds()
            print(f"Finished running \"{cmd}\".")
            print(f"Command execution time(seconds): {print_cmd_exec_time}")
            print("")

        after_execute_datetime = datetime.now()
        print("Finished installing the version.")
        transferring_time = (after_transfer_datetime - before_transfer_datetime).total_seconds()
        execute_time = (after_execute_datetime - after_transfer_datetime).total_seconds()
        total_time = (after_execute_datetime - before_transfer_datetime).total_seconds()

        print("")
        print("Summary:")
        print(f"Transferring time(seconds): {transferring_time}")
        print(f"Execute time(seconds): {execute_time}")
        print(f"Total time(seconds): {total_time}")


if __name__ == "__main__":
    UpgradeScript.new().run()
