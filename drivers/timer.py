import time


class Timer(object):

    @staticmethod
    def get_time():
        return time.time()

    def close(self):
        pass

    def get_current_time(self):
        return self.get_time()
