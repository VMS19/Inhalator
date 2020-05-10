import time

from wd_task import WdTask
from drivers.wd_driver import WdDriver
from scripts.scripts_utils.script import Script


class MuteWD(Script):
    def __init__(self):
        super(MuteWD, self).__init__()
        self._parser.prog = "mute-wd"
        self._parser.description = "Locally mute the WD."

    def _main(self, args, pre_run_variables):
        watchdog = WdDriver()
        while True:
            watchdog.arm()
            time.sleep(WdTask.WD_TIMEOUT)


if __name__ == '__main__':
    MuteWD().run()
