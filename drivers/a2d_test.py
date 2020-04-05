import time
from ads7844_a2d import Ads7844A2D

a2d = Ads7844A2D()
read_tuple = a2d.read()
percentage = read_tuple[1]
feed = read_tuple[2]
print('battery percentage', a2d.battery_percentage(percentage))
print('channel 2 says', feed)
