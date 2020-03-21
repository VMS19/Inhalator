"""Errors module."""


class InhalatorError(BaseException):
    pass


class SFM3200DriverInitError(InhalatorError):
    pass


class FlowSensorNotFoundError(InhalatorError):
    pass


class FlowSensorReadError(InhalatorError):
    pass


class FlowSensorWriteError(InhalatorError):
    pass

class FlowSensorCRCError(InhalatorError):
    pass
