from os import path
from subprocess import Popen
import logging

log = logging.getLogger(__name__)

THIS_FILE = __file__
THIS_DIRECTORY = path.dirname(THIS_FILE)
RESOURCES_DIRECTORY = path.join(THIS_DIRECTORY, "resources")


class SoundDevice:
    BEEP_FILE_PATH = path.join(RESOURCES_DIRECTORY, "beep-3.wav")
    PLAY_CMD = "aplay -q -N {}"

    def __init__(self):
        pass

    def play(self, wav_path):
        Popen(self.PLAY_CMD.format(wav_path), shell=True)
        # Todo: find way to monitor return code of the process. log on failure
        # if ret_code != 0:
        #     log.error("Could not play beep file. apaly returned %d", ret_code)

    def beep(self):
        """Beeps asynchronously."""
        self.play(self.BEEP_FILE_PATH)
