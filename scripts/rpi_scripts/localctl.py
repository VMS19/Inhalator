#!/usr/bin/env python3
from scripts.scripts_utils.scriptsctl import ScriptsCTL
from scripts.rpi_scripts.set_debug_mode import SetDebugMode
from scripts.rpi_scripts.set_rtc_time import SetRTCTime
from scripts.rpi_scripts.mute_wd import MuteWD

if __name__ == "__main__":
    scripts = [
        SetDebugMode(),
        SetRTCTime(),
        MuteWD()
    ]
    ScriptsCTL(scripts=scripts).run()
