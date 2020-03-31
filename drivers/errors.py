"""Errors module."""


class InhalatorError(BaseException):
    pass


class PiGPIOInitError(InhalatorError):
    pass


class I2CDeviceNotFoundError(InhalatorError):
    pass


class FlowSensorReadError(InhalatorError):
    pass


class I2CWriteError(InhalatorError):
    pass

class FlowSensorCRCError(InhalatorError):
    pass

class SPIDriverInitError(InhalatorError):
    pass

class SPIIOError(InhalatorError):
    pass

class I2CReadError(InhalatorError):
    pass


class ConfigurationFileError(BaseException):
    pass