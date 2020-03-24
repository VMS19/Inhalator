"""Errors module."""


class InhalatorError(BaseException):
    pass


class PiGPIOInitError(InhalatorError):
    pass


class I2CDeviceNotFoundError(InhalatorError):
    pass


class I2CReadError(InhalatorError):
    pass


class I2CWriteError(InhalatorError):
    pass


class FlowSensorCRCError(InhalatorError):
    pass


class HCEDriverInitError(InhalatorError):
    pass


class HCEIOError(InhalatorError):
    pass
