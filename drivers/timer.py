import time


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
        from subprocess import check_output
        try:
            out = str(check_output(["cat", "/proc/uptime"]))
            seconds_raw = out.split()[0]
            # seconds without 'b
            seconds_parsed = seconds_raw[2:]
            return int(seconds_parsed)
        except Exception as e:
            # get time.time as backup
            return Timer.get_time()
