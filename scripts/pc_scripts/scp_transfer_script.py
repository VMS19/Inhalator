from script_classes.remote_scp_script import RemoteScpScript


class ScpTransferScript(RemoteScpScript):
    def __init__(self, init=False, parser_args=None):
        super(ScpTransferScript, self).__init__(init=init, parser_args=parser_args)
        self._parser.prog = "Scp-transfer-script"
        self._parser.description = "Transfer files to a remote location via SSH."
        self._parser.add_argument("files", type=str, nargs="+", help="File/s to transfer.")
        self._parser.add_argument("remote_path", type=str, help="Remote's destination path for the file/s.")

    def _main(self):
        """Main logic of the script that inherits the SSH script."""
        self._scp_client.put(files=self._args.files, remote_path=self._args.remote_path)


if __name__ == "__main__":
    ScpTransferScript.new().run()
