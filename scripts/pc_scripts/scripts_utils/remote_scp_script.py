import scp

from .remote_ssh_script import RemoteSSHScript


class RemoteScpScript(RemoteSSHScript):
    def _pre_run(self, args):
        variables = super(RemoteScpScript, self)._pre_run(args)

        scp_client = scp.SCPClient(variables["ssh_client"].get_transport())

        variables["scp_client"] = scp_client

        return variables

    def _post_run(self, args, pre_run_variables):
        if "scp_client" in pre_run_variables and pre_run_variables["scp_client"] is not None:
            pre_run_variables["scp_client"].close()
        super(RemoteScpScript, self)._post_run(args, pre_run_variables)
