from multiprocessing import Process, Queue
import logging
import time

import hce_pressure_sensor
import sfm3200_flow_sensor

log = logging.getLogger(__name__)


class task_manager(object):
	def sensor_sample_loop(self):
		while (True):
			hce_pressure = 1#HcePressureSensor.read_pressure()
			flow_slm = 2#Sfm3200.read_flow_slm()
			self.hce_queue.put(hce_pressure)
			self.flow_queue.put(flow_slm)
			time.sleep(0.05)

	def parse_data_loop(self):
		while (True):
			hce_pressure = self.hce_queue.get()
			flow_slm = self.flow_queue.get()
			print(hce_pressure)
			print(flow_slm)

	def __init__(self):
		self.hce_queue = Queue()
		self.flow_queue = Queue()
		self.sample_sensor_process = Process(target=self.sensor_sample_loop)
		self.parse_data_process = Process(target=self.parse_data_loop)

	def start(self):
		self.sample_sensor_process.start()
		self.parse_data_process.start()




