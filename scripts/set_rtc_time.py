import sys
import os
from drivers.rv8523_rtc import Rv8523Rtc
from datetime import datetime

sys.path.append(os.path.dirname('.'))


def main():
    rtc = None

    try:
        rtc = Rv8523Rtc()
        cur_date = datetime.now()
        print('setting rtc time as ', cur_date)
        rtc.set_rtc_time(cur_date)
    finally:
        if rtc is not None:
            rtc.close()


if __name__ == "__main__":
    main()
