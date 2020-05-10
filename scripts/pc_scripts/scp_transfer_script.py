from scripts_utils.remote_scp_script import RemoteScpScript


class ScpTransferScript(RemoteScpScript):
    def __init__(self):
        super(ScpTransferScript, self).__init__()
        self._parser.prog = "Scp-transfer-script"
        self._parser.description = "Transfer files to a remote location via SSH."
        self._parser.add_argument("files", type=str, nargs="+", help="File/s to transfer.")
        self._parser.add_argument("remote_path", type=str, help="Remote's destination path for the file/s.")

    def _main(self, args, pre_run_variables):
        """Main logic of the script that inherits the SSH script."""
        scp_client = pre_run_variables["scp_client"]
        scp_client.put(files=args.files, remote_path=args.remote_path)


if __name__ == "__main__":
    ScpTransferScript().run()
