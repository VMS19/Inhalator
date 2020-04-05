import time
from ads7844_a2d import Ads7844A2D

a2d = Ads7844A2D()
while True:
    print(a2d.read())
    time.sleep(1)
