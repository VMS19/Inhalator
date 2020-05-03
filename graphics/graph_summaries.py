from graphics.themes import Theme

from tkinter import *


class GraphSummary(object):
    def __init__(self, parent, measurements):
        self.parent = parent
        self.root = parent.element
        self.measurements = measurements

        self.frame = Frame(master=self.root,
                           borderwidth=1)
        self.value_label = Label(master=self.frame, text="HELLO",
                                 font=("Roboto", 17),
                                 bg=Theme.active().BACKGROUND,
                                 fg=self.color())
        self.units_label = Label(master=self.frame, text="HELLO",
                                 font=("Roboto", 8),
                                 bg=Theme.active().BACKGROUND,
                                 fg=self.color())
        self.name_label = Label(master=self.frame, text="HELLO",
                                font=("Roboto", 13),
                                bg=Theme.active().BACKGROUND,
                                fg=self.color())

    def units(self):
        pass

    def name(self):
        pass

    def value(self):
        pass

    def color(self):
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
        return "{}/{}".format(
            round(self.measurements.intake_peak_pressure),
            round(self.measurements.peep_min_pressure))

    def name(self):
        return "PIP/PEEP"

    def units(self):
        return "inH2o"

    def color(self):
        return Theme.active().YELLOW

    def render(self):
        self.frame.place(relx=0, rely=0, relheight=(1/4), relwidth=1)
        super(PressurePeakSummary, self).render()


class VolumeSummary(GraphSummary):
    def value(self):
        return "{}/{}".format(
            int(round(self.measurements.avg_insp_volume)),
            int(round(self.measurements.avg_exp_volume)))

    def name(self):
        return "TVinsp/exp"

    def units(self):
        return "ml"

    def color(self):
        return Theme.active().LIGHT_BLUE

    def render(self):
        self.frame.place(relx=0, rely=(1/4), relheight=(1/4), relwidth=1)
        super(VolumeSummary, self).render()


class BPMSummary(GraphSummary):
    def value(self):
        return f"{round(self.measurements.bpm)}"

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
        return round(self.measurements.o2_saturation_percentage)

    def name(self):
        return "FiO2"

    def units(self):
        return "%"

    def color(self):
        return Theme.active().WHITE

    def render(self):
        self.frame.place(relx=0, rely=(3/4), relheight=(1/4), relwidth=1)
        super(O2SaturationSummary, self).render()
