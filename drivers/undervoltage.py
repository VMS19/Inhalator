from subprocess import check_output


class UnderVoltage(object):
    def read(self):
        output = check_output("/opt/vc/bin/vcgencmd get_throttled".split(" "))
        return int(output[-6:-1], 16) & 1

    def close(self):
        pass