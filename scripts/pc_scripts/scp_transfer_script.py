import argparse

from script_classes.remote_scp_script import RemoteScpScript


class ScpTransferScript(RemoteScpScript):
    _parser = argparse.ArgumentParser(prog="Scp-transfer-script", description="Transfer files to a remote location via SSH.")
    _parser.add_argument("hostname", type=str, help="Remote's hostname/IP.")
    _parser.add_argument("username", type=str, help="Remote's username.")
    _parser.add_argument("password", type=str, help="Remote's password.")
    _parser.add_argument("files", type=str, nargs="+", help="File/s to transfer.")
    _parser.add_argument("remote_path", type=str, help="Remote's destination path for the file/s.")

    def run(self):
        """Main logic of the script that inherits the SSH script."""
        self._scp_client.put(files=self._args.files, remote_path=self._args.remote_path)


if __name__ == "__main__":
    ScpTransferScript.new().run()
