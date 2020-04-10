import time

from drivers.wd_driver import WdDriver
from wd_task import WdTask


def main():
    watchdog = WdDriver()
    while True:
        watchdog.arm()
        time.sleep(WdTask.WD_TIMEOUT)


if __name__ == '__main__':
    main()
