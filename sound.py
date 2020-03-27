import os
import logging
from subprocess import Popen

from data.alerts import AlertCodes

THIS_FILE = __file__
THIS_DIRECTORY = os.path.dirname(THIS_FILE)
RESOURCES_DIRECTORY = os.path.join(THIS_DIRECTORY, "resources")

log = logging.getLogger(__name__)


class SoundDevice(object):
    BEEP_FILE_PATH = os.path.join(RESOURCES_DIRECTORY, "beep-3.wav")
    TIME_BETWEEN_BEEPS = 1
    PLAY_CMD = "aplay -q -N {}"
    PLAY_BEEP_IN_LOOP = "while [ True ] ; do {}; sleep {}; done".format(PLAY_CMD,
                                                                        TIME_BETWEEN_BEEPS)

    def __init__(self, data_store):
        self.store = data_store
        self.alarm_process = None

        self.store.alerts_queue.subscribe(self, self.on_alert)

    def __del__(self):
        self.stop_ringing()

    def play(self, wav_path):
        self.alarm_process = Popen(self.PLAY_BEEP_IN_LOOP.format(wav_path),
                                   shell=True, preexec_fn=os.setsid)

    def ring(self):
        """Beeps asynchronously."""
        self.play(self.BEEP_FILE_PATH)

    def stop_ringing(self):
        try:
            os.killpg(self.alarm_process.pid, 9)
        except:
            pass

    def on_alert(self, alert):
        if alert != AlertCodes.OK:
            self.ring()

        else:
            self.stop_ringing()
