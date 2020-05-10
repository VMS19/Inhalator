"""Contains the abstract script class for scripts that connect to one host via SSH."""
import paramiko

from .script import Script


class RemoteSSHScript(Script):
    """Abstract script class for scripts that connect to one host via SSH."""
    def __init__(self):
        # The argument parser will be set from this call.
        super(RemoteSSHScript, self).__init__()
        self._parser.add_argument("hostname", type=str, help="Remote's hostname/IP.")
        self._parser.add_argument("username", type=str, help="Remote's username.")
        self._parser.add_argument("password", type=str, help="Remote's password.")

    def _pre_run(self, args):
        """
        Add the SSH client variable to the dict of variables and return the dict.
        :param args: the script's arguments passed from the argument parser.
        :return: dict of variables set before running the script's main including the SSH client.
        """
        variables = super(RemoteSSHScript, self)._pre_run(args)

        hostname = args.hostname
        username = args.username
        password = args.password

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy)
        ssh_client.connect(hostname=hostname, username=username, password=password)

        variables["ssh_client"] = ssh_client
        return variables

    def _post_run(self, args, pre_run_variables):
        """
        Close the SSH client.
        :param args: the script's arguments passed from the argument parser.
        :param pre_run_variables: the script's variables set from the pre run function.
        """
        if "ssh_client" in pre_run_variables and pre_run_variables["ssh_client"] is not None:
            pre_run_variables["ssh_client"].close()
        super(RemoteSSHScript, self)._post_run(args, pre_run_variables)
