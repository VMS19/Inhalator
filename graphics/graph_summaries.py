# Tkinter stuff
import platform

from graphics.themes import Theme

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *


class GraphSummary(object):
    def __init__(self, parent, store):
        self.parent = parent
        self.store = store
        self.root = parent.element
        self.frame = Frame(master=self.root)
        self.value_label = Label(master=self.frame, text="HELLO",
                                 font=("Roboto", 18),
                                 bg=Theme.active().SURFACE,
                                 fg=Theme.active().TXT_ON_SURFACE)
        self.units_label = Label(master=self.frame, text="HELLO",
                                 font=("Roboto", 8),
                                 bg=Theme.active().SURFACE,
                                 fg=Theme.active().TXT_ON_SURFACE)
        self.name_label = Label(master=self.frame, text="HELLO",
                                font=("Roboto", 15),
                                 bg=Theme.active().SURFACE,
                                 fg=Theme.active().TXT_ON_SURFACE)

    def units(self):
        pass

    def name(self):
        pass

    def value(self):
        pass

    def render(self):
        self.units_label.configure(text="({})".format(self.units()))
        self.value_label.configure(text=self.value())
        self.name_label.configure(text=self.name())

        self.value_label.place(relx=0, relwidth=1, relheight=0.45, rely=0)
        self.units_label.place(relx=0, relwidth=1, relheight=0.08, rely=0.45)
        self.name_label.place(relx=0, relwidth=1, relheight=0.47, rely=0.53)

    def update(self):
        self.value_label.configure(text=self.value())


class PressurePeakSummary(GraphSummary):
    def value(self):
        return "{:.0f}".format(self.store.intake_peak_pressure)

    def name(self):
        return "pPeak"

    def units(self):
        return "cmH2O"

    def render(self):
        self.frame.place(relx=0, rely=0, relheight=(1/3), relwidth=1)
        super(PressurePeakSummary, self).render()


class VolumeSummary(GraphSummary):
    def value(self):
        return "{:.0f}".format(self.store.volume)

    def name(self):
        return "Volume"

    def units(self):
        return "ml"

    def render(self):
        self.frame.place(relx=0, rely=(1/3), relheight=(1/3), relwidth=1)
        super(VolumeSummary, self).render()


class BPMSummary(GraphSummary):
    def value(self):
        return "{:.0f}".format(self.store.bpm)

    def name(self):
        return "bpm"

    def units(self):
        return "Rate"

    def render(self):
        self.frame.place(relx=0, rely=(2/3), relheight=(1/3), relwidth=1)
        super(BPMSummary, self).render()
