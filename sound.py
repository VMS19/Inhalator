import os

THIS_FILE = __file__
THIS_DIRECTORY = os.path.dirname(THIS_FILE)
RESOURCES_DIRECTORY = os.path.join(THIS_DIRECTORY, "resources")


class SoundDevice:
    BEEP_FILE_PATH = os.path.join(RESOURCES_DIRECTORY, "beep-3.wav")

    @staticmethod
    def beep():
        """Beeps asynchronously."""
        os.system("aplay -q %s" % SoundDevice.BEEP_FILE_PATH)
