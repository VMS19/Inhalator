#!/usr/bin/env python3
"""Control all the local RPi scripts."""

from scripts.scripts_utils.scriptsctl import ScriptsCTL
from scripts.rpi_scripts.set_debug_mode import SetDebugMode
from scripts.rpi_scripts.update_rtc_time import UpdateRTCTime
from scripts.rpi_scripts.mute_wd import MuteWD

if __name__ == "__main__":
    scripts = [
        SetDebugMode(),
        UpdateRTCTime(),
        MuteWD()
    ]
    # Initiate a new scripts control script with all of the scripts.
    # Run it with no arguments - meaning it will be given from the CLI.
    ScriptsCTL(scripts=scripts).run()
