# Tkinter stuff
import platform

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

from graphics.panes import MasterFrame


class GUI(object):
    """GUI class for Inhalator"""
    TEXT_SIZE = 10

    def __init__(self, data_store, watchdog):
        self.store = data_store
        self.root = Tk()
        self.root.title("Inhalator")
        self.root.geometry('800x480')
        self.root.attributes("-fullscreen", True)
        self.master_frame = MasterFrame(self.root, watchdog, store=self.store)

    def exitProgram(self, sig, _):
        self.root.quit()

    def render(self):
        self.master_frame.render()

    def gui_update(self):
        self.root.update()
        self.root.update_idletasks()
        self.master_frame.update()