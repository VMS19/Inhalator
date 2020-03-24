# Tkinter stuff
import platform

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *


class GraphSummary(object):
    def __init__(self, parent, store):
        self.parent = parent
        self.store = store
        self.root = parent.element

        self.label = Label(master=self.root, text="HELLO", font=("Tahoma", 40), bg="white")

    @property
    def element(self):
        return self.label

    def render(self):
        pass

    def update(self):
        pass


class PressurePeakSummary(GraphSummary):
    def render(self):
        self.label.configure(text="525\n(ml)\nVte", borderwidth=1, relief="groove")
        self.label.place(relx=0, rely=0.025, relheight=0.3, relwidth=1)

class AirOutputSummary(GraphSummary):
    def render(self):
        self.label.configure(text="7\n(bpm)\nRate", borderwidth=1, relief="groove")
        self.label.place(relx=0, rely=0.35, relheight=0.3, relwidth=1)

class BPMSummary(GraphSummary):
    def render(self):
        self.label.configure(text="31\n(cmH2O)\npPeak", borderwidth=1, relief="groove")
        self.label.place(relx=0, rely=0.675, relheight=0.3, relwidth=1)
