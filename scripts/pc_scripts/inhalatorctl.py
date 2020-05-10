#!/usr/bin/env python3
from scripts.scripts_utils.scriptsctl import ScriptsCTL
from get_mac import GetMAC
from ftp_save_logs import FTPSaveLogs
from set_debug_mode import SetDebugMode
from remote_wd_mute import RemoteWDMute
from upgrade_script import UpgradeScript
from remote_rtc_update import RemoteRTCUpdate
from scp_transfer import ScpTransfer


class InhalatorCTL(ScriptsCTL):
    def __init__(self, scripts):
        super(InhalatorCTL, self).__init__(scripts)
        self._parser.prog = "inhalator-ctl"
        self._parser.description = "Control all remote scripts for the inhalator."
        self._parser.add_argument("hostname", type=str, help="Remote's hostname/IP.")
        self._parser.add_argument("username", type=str, help="Remote's username.")
        self._parser.add_argument("password", type=str, help="Remote's password.")

    def _main(self, args, pre_run_variables):
        if args.run_scripts:
            ssh_args = (args.hostname, args.username, args.password)
            ssh_common_arguments = " ".join(ssh_args)
            if args.common_arguments:
                args.common_arguments = ssh_common_arguments + args.common_arguments
            else:
                args.common_arguments = ssh_common_arguments
        super(InhalatorCTL, self)._main(args, pre_run_variables)


if __name__ == "__main__":
    scripts = [
        GetMAC(),
        FTPSaveLogs(),
        SetDebugMode(),
        RemoteWDMute(),
        UpgradeScript(),
        RemoteRTCUpdate(),
        ScpTransfer()
    ]
    InhalatorCTL(scripts=scripts).run()
