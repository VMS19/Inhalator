import os
import sys
from datetime import datetime

from drivers.rv8523_rtc import Rv8523Rtc
from scripts.scripts_utils.script import Script

sys.path.append(os.path.dirname('.'))


class UpdateRTCTime(Script):
    """Script that updates the hardware RTC time by the current datetime."""
    def __init__(self):
        super(UpdateRTCTime, self).__init__()
        self._parser.prog = "update-rtc-time"
        self._parser.description = "Update the RTC time by the current datetime."

    def _main(self, args, pre_run_variables):
        """
        Update the RTC time according to the current datetime.
        :param args: the script's arguments passed from the argument parser.
        :param pre_run_variables: the script's variables set from the pre run function.
        """
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
    UpdateRTCTime().run()
