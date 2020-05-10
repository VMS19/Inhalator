import os
import sys
from datetime import datetime

from drivers.rv8523_rtc import Rv8523Rtc
from scripts.scripts_utils.script import Script

sys.path.append(os.path.dirname('.'))


class SetRTCTime(Script):
    def __init__(self):
        super(SetRTCTime, self).__init__()
        self._parser.prog = "set-RTC-time"
        self._parser.description = "Set the RTC time."

    def _main(self, args, pre_run_variables):
        rtc = None
        try:
            rtc = Rv8523Rtc()
            current_datetime = datetime.now()
            print('setting rtc time as ', current_datetime)
            rtc.set_rtc_time(current_datetime)
        finally:
            if rtc is not None:
                rtc.close()


if __name__ == '__main__':
    SetRTCTime().run()
