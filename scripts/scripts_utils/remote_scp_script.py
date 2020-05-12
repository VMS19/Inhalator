"""Contains the abstract script class for scripts that connect to one host via SSH and require SCP."""
import scp

from .remote_ssh_script import RemoteSSHScript


class RemoteScpScript(RemoteSSHScript):
    """Abstract script class for scripts that connect to one host via SSH and require SCP."""
    def _pre_run(self, args):
        """
        Add the SCP client variable to the dict of variables and return the dict.
        :param args: the script's arguments passed from the argument parser.
        :return: dict of variables set before running the script's main including the SCP client.
        """
        variables = super(RemoteScpScript, self)._pre_run(args)
        scp_client = scp.SCPClient(variables["ssh_client"].get_transport())
        variables["scp_client"] = scp_client
        return variables

    def _post_run(self, args, pre_run_variables):
        """
        Close the SCP client.
        :param args: the script's arguments passed from the argument parser.
        :param pre_run_variables: the script's variables set from the pre run function.
        """
        if "scp_client" in pre_run_variables and pre_run_variables["scp_client"] is not None:
            pre_run_variables["scp_client"].close()
        super(RemoteScpScript, self)._post_run(args, pre_run_variables)
