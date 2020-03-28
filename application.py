# Tkinter stuff
import platform

if platform.python_version() < '3':
    from Tkinter import *
else:
    from tkinter import *

from graphics.panes import MasterFrame
from graphics.themes import Theme, DarkTheme


class Application(object):
    """The Inhalator application"""
    TEXT_SIZE = 10

    __instance = None  # shared instance

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    @classmethod
    def instance(cls):
        return cls.__instance

    def __init__(self, measurements, events, watchdog, drivers):
        self.should_run = True
        self.root = Tk()
        self.theme = Theme.toggle_theme()  # Set to dark mode, TODO: Make this configurable
        self.root.protocol("WM_DELETE_WINDOW", self.exit)  # Catches Alt-F4
        self.root.title("Inhalator")
        self.root.geometry('800x480')
        self.root.attributes("-fullscreen", True)
        self.master_frame = MasterFrame(self.root, watchdog=watchdog,
                                        measurements=measurements,
                                        events=events,
                                        drivers=drivers)

    def exit(self):
        self.root.quit()
        self.should_run = False

    def render(self):
        self.master_frame.render()

    def gui_update(self):
        self.root.update()
        self.root.update_idletasks()
        self.master_frame.update()
