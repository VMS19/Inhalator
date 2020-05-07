import paramiko

from .script import Script


class RemoteSSHScript(Script):
    def __init__(self, init=False, parser_args=None):
        super(RemoteSSHScript, self).__init__(init=init, parser_args=parser_args)
        self._parser.add_argument("hostname", type=str, help="Remote's hostname/IP.")
        self._parser.add_argument("username", type=str, help="Remote's username.")
        self._parser.add_argument("password", type=str, help="Remote's password.")
        if init:
            hostname = self._args.hostname
            username = self._args.username
            password = self._args.password
            self._ssh_client = paramiko.SSHClient()
            self._ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy)
            self._ssh_client.connect(hostname=hostname, username=username, password=password)

    def __del__(self):
        if self._initiated and hasattr(self, '_ssh_client') and self._ssh_client is not None:
            self._ssh_client.close()
