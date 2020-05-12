from scripts.scripts_utils import consts
from scripts.scripts_utils.remote_ssh_script import RemoteSSHScript


def print_stream_lines(stream_name, stream):
    lines = stream.readlines()

    if len(lines):
        print(f"+---{stream_name}---:")

    for line in lines:
        print(line)

    if len(lines):
        print(f"+-------------")


class SetDebugMode(RemoteSSHScript):
    """Script that set the debug mode of the remote inhalator."""
    def __init__(self):
        super(SetDebugMode, self).__init__()
        self._parser.prog = "set-debug-mode"
        self._parser.description = "Toggle the inhalator software debug mode(ON->OFF, OFF->ON)."
        self._parser.add_argument("--debug", action="store_true",
                                  help="Whether to enable debug mode or not")

    def _main(self, args, pre_run_variables):
        """Set the debug mode of the remote inhalator."""
        ssh_client = pre_run_variables["ssh_client"]

        set_debug_mode_parameters = "--debug" if args.debug else ""
        set_debug_mode_cmdline = f"sudo PYTHONPATH={consts.INHALATOR_REPO_FOLDER_PATH} python3 {consts.INHALATOR_REPO_FOLDER_PATH}/{consts.RPI_SCRIPTS_FOLDER}/set_debug_mode.py {set_debug_mode_parameters}"

        print("Running set_debug_mode!")
        print(f"Executing: '{set_debug_mode_cmdline}'")
        _, stdout, stderr = ssh_client.exec_command(set_debug_mode_cmdline)
        print_stream_lines("stdout", stdout)
        print_stream_lines("stderr", stderr)
        print("Done!")

        print("Restarting proftpd!")
        _, stdout, stderr = ssh_client.exec_command("sudo service proftpd restart")
        print_stream_lines("stdout", stdout)
        print_stream_lines("stderr", stderr)
        print("Done!")


if __name__ == "__main__":
    SetDebugMode().run()
