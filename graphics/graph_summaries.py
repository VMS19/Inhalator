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
        self.frame = Frame(master=self.root, bg="white")
        self.value_label = Label(master=self.frame, text="HELLO",
                                 font=("Tahoma", 30), bg="white")
        self.units_label = Label(master=self.frame, text="HELLO",
                                 font=("Tahoma", 8), bg="white")
        self.name_label = Label(master=self.frame, text="HELLO",
                                font=("Tahoma", 30), bg="white")

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

        self.value_label.place(relx=0, relwidth=1, relheight=0.45, rely=0.09)
        self.units_label.place(relx=0, relwidth=1, relheight=0.08, rely=0.56)
        self.name_label.place(relx=0, relwidth=1, relheight=0.25, rely=0.75)

    def update(self):
        self.value_label.configure(text=self.value())


class PressurePeakSummary(GraphSummary):
    def value(self):
        return "{:.2f}".format(self.parent.parent.center_pane.pressure_graph.pressure_display_values[-1])

    def name(self):
        return "pPeak"

    def units(self):
        return "cmH2O"

    def render(self):
        self.frame.place(relx=0, rely=0.025, relheight=0.3, relwidth=1)
        super(PressurePeakSummary, self).render()


class VolumeSummary(GraphSummary):
    def value(self):
        return "{:.5f}".format(self.store.volume)

    def name(self):
        return "Volume"

    def units(self):
        return "ml"

    def render(self):
        self.frame.place(relx=0, rely=0.35, relheight=0.3, relwidth=1)
        super(VolumeSummary, self).render()


class BPMSummary(GraphSummary):
    def value(self):
        return 7

    def name(self):
        return "bpm"

    def units(self):
        return "Rate"

    def render(self):
        self.frame.place(relx=0, rely=0.675, relheight=0.3, relwidth=1)
        super(BPMSummary, self).render()
