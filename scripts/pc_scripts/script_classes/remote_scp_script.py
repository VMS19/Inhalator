import scp

from .remote_ssh_script import RemoteSSHScript


class RemoteScpScript(RemoteSSHScript):
    def __init__(self, init=False, parser_args=None):
        super(RemoteScpScript, self).__init__(init=init, parser_args=parser_args)
        if init:
            self._scp_client = scp.SCPClient(self._ssh_client.get_transport())

    def __del__(self):
        if self._initiated and hasattr(self, '_scp_client') and self._scp_client is not None:
            self._scp_client.close()
