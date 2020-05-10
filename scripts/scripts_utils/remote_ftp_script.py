"""Contains the abstract script class for scripts that connect to one host via FTP."""
import ftplib

from .script import Script


class RemoteFTPScript(Script):
    """Abstract script class for scripts that connect to one host via FTP."""
    def __init__(self):
        super(RemoteFTPScript, self).__init__()
        self._parser.add_argument("hostname", type=str, help="Remote's hostname/IP.")
        self._parser.add_argument("username", type=str, help="Remote's username.")
        self._parser.add_argument("password", type=str, help="Remote's password.")

    def _pre_run(self, args):
        """
        Add the FTP client variable to the dict of variables and return the dict.
        :param args: the script's arguments passed from the argument parser.
        :return: dict of variables set before running the script's main including the FTP client.
        """
        variables = super(RemoteFTPScript, self)._pre_run(args)
        ftp_client = ftplib.FTP(args.hostname, user=args.username, passwd=args.password)
        variables["ftp_client"] = ftp_client
        return variables

    def _post_run(self, args, pre_run_variables):
        """
        Close the FTP client.
        :param args: the script's arguments passed from the argument parser.
        :param pre_run_variables: the script's variables set from the pre run function.
        """
        if "ftp_client" in pre_run_variables and pre_run_variables["ftp_client"] is not None:
            pre_run_variables["ftp_client"].close()
        super(RemoteFTPScript, self)._post_run(args, pre_run_variables)
