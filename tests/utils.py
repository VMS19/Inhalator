import os
import csv
import time

THIS_DIRECTORY = os.path.dirname(__file__)

class SamplesCSVParser(object):
    FLOW = "flow"
    OXYGEN = "oxygen"
    PRESSURE = "pressure"
    TIME_ELAPSED = "time elapsed (seconds)"
    COLUMNS = [TIME_ELAPSED, PRESSURE, FLOW, OXYGEN]

    PIG_DATA_PATH = os.path.join(os.path.dirname(THIS_DIRECTORY),
                                 "drivers", "mocks", "pig_data.csv")

    def __init__(self, csv_path=PIG_DATA_PATH):
        self.pressure_samples = []
        self.flow_samples = []
        self.oxygen_samples = []
        self.time = []

        now = time.time()

        csv_file = open(csv_path)
        reader = csv.DictReader(csv_file, fieldnames=self.COLUMNS)

        next(reader)  # First line is headers which we don't need

        for line in reader:
            self.pressure_samples.append(float(line[self.PRESSURE]))
            self.flow_samples.append(float(line[self.FLOW]))
            self.time.append(now + float(line[self.TIME_ELAPSED]))
            self.oxygen_samples.append(float(line[self.OXYGEN]))

        csv_file.close()

    def samples(self, start=None, end=None):
        start = start or 0
        end = end or len(self.time)

        yield from zip(self.time[start:end],
                       self.pressure_samples[start:end],
                       self.flow_samples[start:end],
                       self.oxygen_samples[start:end])
