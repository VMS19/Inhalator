# Tkinter stuff
import platform

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

from graphics.threshold_prompt import ThresholdPrompt


class ThresholdButton(object):
    def __init__(self, parent, store):
        self.parent = parent
        self.store = store
        self.root = parent.element

        self.button = Button(self.root, text="<PLACEHOLDER>", command=self.on_click)
        self.label = Label(self.root, text="<PLACEHOLDER>", bg="white"  )
        self.button.config(font=("Tahoma", 22))

    def button_text(self):
        pass

    def on_click(self):
        pass

    def render(self):
        pass

    def disable(self):
        self.button.configure(state="disabled")

    def enable(self):
        self.button.configure(state="normal")

    def update(self):
        self.button.configure(text=self.button_text())


class BPMThresholdButton(ThresholdButton):
    def render(self):
        # self.button.place(relx=(0.5 / 6), rely=0, relheight=1, relwidth=0.1)
        pass

class VolumeThresholdButton(ThresholdButton):
    def button_text(self):
        return "L={}\nH={}".format(self.store.flow_min_threshold.value,
                                       self.store.flow_max_threshold.value)

    def on_click(self):
        prompt = ThresholdPrompt(self.root, self.store, self.store.flow_min_threshold,
                                 self.store.flow_max_threshold, self.update)

        prompt.show()

    def label_text(self):
        return "Volume"

    def render(self):
        self.button.place(relx=(0.5 / 6) * 2 + 0.1, rely=0, relheight=0.6, relwidth=0.1)
        self.button.configure(text=self.button_text())
        self.label.place(relx=(0.5 / 6) * 2 + (0.1), rely=0.7, relheight=0.3, relwidth=0.1)
        self.label.configure(text=self.label_text())


class PeakFlowThresholdButton(ThresholdButton):
    def render(self):
        # self.button.place(relx=(0.5 / 6) * 3 + (0.1) * 2, rely=0, relheight=1, relwidth=0.1)
        # self.button.configure(text=self.store.flow_max_threshold.value)
        pass

class PEEPThresholdButton(ThresholdButton):

    def button_text(self):
        return "L={}\nH={}".format(self.store.pressure_min_threshold.value,
                                       self.store.pressure_max_threshold.value)

    def label_text(self):
        return "PEEP"

    def on_click(self):
        prompt = ThresholdPrompt(self.root, self.store, self.store.pressure_min_threshold,
                                 self.store.pressure_max_threshold, self.update)

        prompt.show()

    def render(self):
        self.button.place(relx=(0.5 / 6) * 4 + (0.1) * 3, rely=0, relheight=0.6, relwidth=0.1)
        self.button.configure(text=self.button_text())
        self.label.place(relx=(0.5 / 6) * 4 + (0.1) * 3, rely=0.7, relheight=0.3, relwidth=0.1)
        self.label.configure(text=self.label_text())

class O2ThresholdButton(ThresholdButton):
    def render(self):
        # self.button.place(relx=(0.5 / 6) * 5 + (0.1) * 4, rely=0, relheight=1, relwidth=0.1)
        pass
