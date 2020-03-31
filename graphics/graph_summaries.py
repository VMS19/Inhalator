# Tkinter stuff
import platform

from graphics.themes import Theme

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *


class GraphSummary(object):
    def __init__(self, parent, measurements):
        self.parent = parent
        self.root = parent.element
        self.measurements = measurements

        self.frame = Frame(master=self.root,
                           borderwidth=1)
        self.value_label = Label(master=self.frame, text="HELLO",
                                 font=("Roboto", 18),
                                 bg=self.color(),
                                 fg=Theme.active().TXT_ON_SURFACE)
        self.units_label = Label(master=self.frame, text="HELLO",
                                 font=("Roboto", 8),
                                 bg=self.color(),
                                 fg=Theme.active().TXT_ON_SURFACE)
        self.name_label = Label(master=self.frame, text="HELLO",
                                font=("Roboto", 15),
                                bg=self.color(),
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
        return "{:.0f}".format(self.measurements.intake_peak_pressure)

    def name(self):
        return "pPeak"

    def units(self):
        return "cmH2O"

    def color(self):
        return Theme.active().YELLOW

    def render(self):
        self.frame.place(relx=0, rely=0, relheight=(1/4), relwidth=1)
        super(PressurePeakSummary, self).render()


class VolumeSummary(GraphSummary):
    def value(self):
        return "{:.0f}".format(self.measurements.volume)

    def name(self):
        return "Volume"

    def units(self):
        return "ml"

    def color(self):
        return Theme.active().LIGHT_BLUE

    def render(self):
        self.frame.place(relx=0, rely=(1/4), relheight=(1/4), relwidth=1)
        super(VolumeSummary, self).render()


class BPMSummary(GraphSummary):
    def value(self):
        return "{:.0f}".format(self.measurements.bpm)

    def name(self):
        return "Rate"

    def units(self):
        return "bpm"

    def color(self):
        return Theme.active().LIGHT_BLUE

    def render(self):
        self.frame.place(relx=0, rely=(2/4), relheight=(1/4), relwidth=1)
        super(BPMSummary, self).render()


class O2SaturationSummary(GraphSummary):
    def value(self):
        # Round to nearest half
        return "{:.2f}".format(
            round(self.measurements.o2_saturation_percentage * 2) / 2)

    def name(self):
        return "FiO2"

    def units(self):
        return "%"

    def color(self):
        return "green"

    def render(self):
        self.frame.place(relx=0, rely=(3/4), relheight=(1/4), relwidth=1)
        super(O2SaturationSummary, self).render()
