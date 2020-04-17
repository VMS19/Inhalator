import time


class Timer(object):

    HOURS_TO_SECONDS = 60 * 60

    @staticmethod
    def get_time():
        return time.time()

    def close(self):
        pass

    def get_current_time(self):
        return self.get_time()

    def sleep(self, amount):
        return time.sleep(amount)
