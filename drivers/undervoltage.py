import re
from subprocess import check_output


class UnderVoltage(object):
    def read(self):
        output = check_output("/opt/vc/bin/vcgencmd get_throttled".split(" "))
        status_register = re.findall("\d+$", output)[0]
        return int(status_register, 16) & 1

    def close(self):
        pass