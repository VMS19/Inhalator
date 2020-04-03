from itertools import cycle


class MockTimer(object):

    def __init__(self, time_series):
        if not hasattr(time_series, "__getitem__"):
            time_series = list(time_series)
        # We can't just cycle over the timestamp, because it doesn't make sense
        # for time to wrap around. But it does make sense to cycle over the
        # _intervals_ between the timestamps.
        intervals = [j - i for i, j in zip(time_series[:-1], time_series[1:])]
        self.intervals = cycle(intervals)
        self.current_time = time_series[0]

    def get_time(self):
        current = self.current_time
        self.current_time += next(self.intervals)
        return current
