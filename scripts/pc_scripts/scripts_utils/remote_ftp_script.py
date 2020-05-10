import ftplib

from .script import Script


class RemoteFTPScript(Script):
    def __init__(self):
        super(RemoteFTPScript, self).__init__()
        self._parser.add_argument("hostname", type=str, help="Remote's hostname/IP.")
        self._parser.add_argument("username", type=str, help="Remote's username.")
        self._parser.add_argument("password", type=str, help="Remote's password.")

    def _pre_run(self, args):
        variables = super(RemoteFTPScript, self)._pre_run(args)
        ftp_client = ftplib.FTP(args.hostname, user=args.username, passwd=args.password)
        variables["ftp_client"] = ftp_client
        return variables

    def _post_run(self, args, pre_run_variables):
        if "ftp_client" in pre_run_variables and pre_run_variables["ftp_client"] is not None:
            pre_run_variables["ftp_client"].close()
        super(RemoteFTPScript, self)._post_run(args, pre_run_variables)
