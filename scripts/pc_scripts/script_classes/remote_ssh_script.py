import paramiko

from .script import Script
import abc


class RemoteSSHScript(Script):
    def __init__(self, parser_args=None):
        super(RemoteSSHScript, self).__init__(parser_args)
        hostname = self._args.hostname
        username = self._args.username
        password = self._args.password
        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.set_missing_host_key_policy(paramiko.WarningPolicy)
        self._ssh_client.connect(hostname=hostname, username=username, password=password)

    def __del__(self):
        if hasattr(self, '_ssh_client') and self._ssh_client is not None:
            self._ssh_client.close()
