import os
import logging
from subprocess import Popen


THIS_FILE = __file__
THIS_DIRECTORY = os.path.dirname(THIS_FILE)
RESOURCES_DIRECTORY = os.path.join(THIS_DIRECTORY, "resources")


log = logging.getLogger(__name__)


class SoundDevice(object):
    BEEP_FILE_PATH = os.path.join(RESOURCES_DIRECTORY, "beep-3.wav")
    PLAY_CMD = "aplay -q -N {}"

    @classmethod
    def play(cls, wav_path):
        Popen(cls.PLAY_CMD.format(wav_path), shell=True)
        # Todo: find way to monitor return code of the process. log on failure
        # if ret_code != 0:
        #     log.error("Could not play beep file. apaly returned %d", ret_code)

    @classmethod
    def beep(cls):
        """Beeps asynchronously."""
        cls.play(cls.BEEP_FILE_PATH)
