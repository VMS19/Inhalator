import errors

class NullDriver(object):
    def read(self):
        raise errors.I2CDeviceNotFoundError()

    def close(self):
    	pass