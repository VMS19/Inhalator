from scripts.scripts_utils.remote_ssh_script import RemoteSSHScript


GET_MAC_CMDLINE = "cat /sys/class/net/eth0/address"


def print_stream_lines(stream_name, stream):
    lines = stream.readlines()

    if len(lines):
        print(f"+---{stream_name}---:")

    for line in lines:
        print(line)

    if len(lines):
        print(f"+-------------")


class GetMAC(RemoteSSHScript):
    def __init__(self):
        super(GetMAC, self).__init__()
        self._parser.prog = "get-mac"
        self._parser.description = "Get remote's MAC address."

    def _main(self, args, pre_run_variables):
        """Main logic of the script that inherits the SSH script."""
        ssh_client = pre_run_variables["ssh_client"]

        _, stdout, stderr = ssh_client.exec_command(GET_MAC_CMDLINE)
        print_stream_lines("stdout", stdout)
        print_stream_lines("stderr", stderr)


if __name__ == "__main__":
    GetMAC().run()
