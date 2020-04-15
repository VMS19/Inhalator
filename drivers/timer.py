import time
import sh

class Timer(object):

    @staticmethod
    def get_time():
        return time.time()

    def close(self):
        pass

    def get_current_time(self):
        return self.get_time()

    def sleep(self, amount):
        return time.sleep(amount)

    @staticmethod
    def get_sys_uptime():
        try:
            uptime = sh.uptime()
            # uptime format, take only seconds.
            #' 21:10:00 up 1 day,  1:27,  1 user,  load average: 0.61, 0.74, 0.83\n'
            seconds = uptime.stdout[7:9]
            return int(seconds)
        except Exception:
            # get time.time as backup
            return Timer.get_time()
