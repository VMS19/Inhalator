import sys
sys.path.append('..')

from drivers.rv8523_rtc import Rv8523Rtc
from datetime import datetime


def main():
    rtc = Rv8523Rtc()
    cur_date = datetime.datetime.now()
    print('setting rtc time as ', cur_date)
    rtc.set_time(cur_date)


if __name__ == "__main__":
    main()
