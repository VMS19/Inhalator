import logging
from rv8523_rtc import Rv8523Rtc


def main():
    logging.basicConfig(level=logging.DEBUG)
    rtc = None

    try:
        rtc = Rv8523Rtc()
        print(rtc.read())
    finally:
        if rtc is not None:
            rtc.close()


if __name__ == "__main__":
    main()
