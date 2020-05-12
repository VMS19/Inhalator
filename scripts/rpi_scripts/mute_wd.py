"""Mute the hardware WD."""
import time

from wd_task import WdTask
from drivers.wd_driver import WdDriver
from scripts.scripts_utils.script import Script


class MuteWD(Script):
    """Script that mute the hardware WD."""
    def __init__(self):
        super(MuteWD, self).__init__()
        self._parser.prog = "mute-wd"
        self._parser.description = "Locally mute the WD."

    def _main(self, args, pre_run_variables):
        """
        Mute the hardware WD.
        :param args: the script's arguments passed from the argument parser.
        :param pre_run_variables: the script's variables set from the pre run function.
        """
        watchdog = WdDriver()
        while True:
            watchdog.arm()
            time.sleep(WdTask.WD_TIMEOUT)


if __name__ == '__main__':
    MuteWD().run()
