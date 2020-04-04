import os
import logging
from subprocess import Popen

THIS_FILE = __file__
THIS_DIRECTORY = os.path.dirname(THIS_FILE)
PARENT_DIRECTORY = os.path.dirname(THIS_DIRECTORY)
RESOURCES_DIRECTORY = os.path.join(PARENT_DIRECTORY, "resources")

log = logging.getLogger(__name__)


class SoundViaAux(object):
    BEEP_FILE_PATH = os.path.join(RESOURCES_DIRECTORY, "beep-3.wav")
    TIME_BETWEEN_BEEPS = 0.1
    PLAY_BEEP_IN_LOOP = "while [ True ] ; do aplay -q -N {wav_path}; sleep {frequency}; done"
    SET_AUX_CMD = "amixer cset numid=3 1"

    __instance = None  # shared instance

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            instance = cls()
            cls.__instance = instance
            return instance

        return cls.__instance

    def __init__(self):
        self.alarm_process = None
        self.is_playing = False
        os.system(self.SET_AUX_CMD)

    def close(self):
        self.stop()

    def __del__(self):
        self.stop()

    def _play(self, wav_path, frequency):
        command = self.PLAY_BEEP_IN_LOOP.format(frequency=frequency, wav_path=wav_path)

        # We assign the created process as the session leader right before
        # the kernel forks() for a new process, so that we can kill the shell and any
        # process it will spawn in the future
        self.alarm_process = Popen(command, shell=True, preexec_fn=os.setsid)

    def start(self, frequency=TIME_BETWEEN_BEEPS):
        """Beeps asynchronously."""
        if not self.is_playing:
            self._play(self.BEEP_FILE_PATH, frequency)
            self.is_playing = True

    def stop(self):
        try:
            os.killpg(self.alarm_process.pid, 9)
            self.is_playing = False

        except:
            pass
