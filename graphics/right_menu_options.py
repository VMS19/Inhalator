# Tkinter stuff
import platform

if platform.python_version() < '3':
    from Tkinter import *

else:
    from tkinter import *

from graphics.themes import Theme

class ClearAlertsButton(object):
    def __init__(self, parent, store):
        self.parent = parent
        self.root = parent.element
        self.store = store

        self.button = Button(master=self.root,
                             command=self.on_click,
                             font=("Roboto", 20),
                             relief="flat",
                             bg="#3c3149", fg="#d7b1f9",
                             activebackground="#433850",
                             activeforeground="#e3e1e5",
                             text="Clear")

    def on_click(self):
        self.store.alerts_queue.clear_alerts()

    def render(self):
        self.button.place(relx=0, rely=0.1, relwidth=0.8, relheight=0.2)

    def update(self):
        pass

class MuteAlertsButton(object):
    def __init__(self, parent, store):
        self.parent = parent
        self.root = parent.element
        self.store = store

        self.button = Button(master=self.root,
                             command=self.on_click,
                             font=("Roboto", 20),
                             text="Mute",
                             relief="flat",
                             bg="#3c3149", fg="#d7b1f9",
                             activebackground="#433850",
                             activeforeground="#e3e1e5",)

    def on_click(self):
        print("Not Implemented Yet")

    def render(self):
        self.button.place(relx=0, rely=0.4, relwidth=0.8, relheight=0.2)

    def update(self):
        pass

class LockThresholdsButton(object):
    def __init__(self, parent, store):
        self.parent = parent
        self.root = parent.element
        self.store = store

        self.button = Button(master=self.root,
                             command=self.on_click,
                             text="Lock",relief="flat",
                             font=("Roboto", 20),
                             bg="#3c3149", fg="#d7b1f9",
                             activebackground="#433850",
                             activeforeground="#e3e1e5",)

    def on_click(self):
        print("Not Implemented Yet")

    def render(self):
        self.button.place(relx=0, rely=0.75, relwidth=0.8, relheight=0.2)

    def update(self):
        pass