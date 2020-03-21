import spidev

class hce_pressure_sensor: 
	SPI_BUS = 0x0
	SPI_DEV = 0x0
	SPI_CLK_SPEED_KHZ = 2500000 # 100-640khz
	SPI_MODE = 0x00 # Default CPOL-0 CPHA-0 
	PERIPHERAL_MINIMAL_DELAY = 0.05 # 5 milli, but really is 5 micro
	MOSI_DATA = 0xFF # HIGH values are needed, otherwise undefined behaviour
	SPI_READ_CMD = [MOSI_DATA] * 3
	# change names of these
	MAX_PRESSURE = #operating pressure? page 2
	MIN_PRESSURE =
	MAX_OUT_PRESSURE = # Output? page 3
	MIN_OUT_PRESSURE =
	SENSITIVITY = (MAX_OUT_PRESSURE - MIN_OUT_PRESSURE)/(MAX_PRESSURE - MIN_PRESSURE)

	def __init__(self):
		self._spi = spidev.SpiDev()
		self._spi.open(SPI_BUS, SPI_DEV)
		self._spi.max_speed_hz = SPI_CLK_SPEED_KHZ
		self._spi.mode = SPI_MODE

	def calculate_pressure(pressure_reading):
		return (((pressure_reading - MIN_OUT_PRESSURE)/SENSITIVITY) + MIN_PRESSURE)

	def read_pressure(self):
		pressure_raw = self._spi.xfer(SPI_READ_CMD, PERIPHERAL_MINIMAL_DELAY * 10)
		pressure_reading = (raw_pressure[1] << 16) | (raw_pressure[2])
		pressure_parsed = calculate_pressure(pressure_reading)
		return pressure_parsed



