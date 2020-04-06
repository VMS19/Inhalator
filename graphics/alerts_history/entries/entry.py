from tkinter import Frame, Label

from graphics.themes import Theme


class AlertEntry(object):
    def __init__(self, root, index, total_alerts_in_screen):
        self.root = root
        self.index = index
        self.total_alerts_in_screen = total_alerts_in_screen

        self.relheight = 1 / self.total_alerts_in_screen
        self.rely = self.relheight * self.index

        self.frame = Frame(master=self.root,
                           highlightbackground="white",
                           highlightcolor="white",
                           highlightthickness=1)

        self.index_label = Label(master=self.frame,
                                bg=Theme.active().SURFACE,
                                fg=Theme.active().TXT_ON_SURFACE)

        self.time_label = Label(master=self.frame,
                                bg=Theme.active().SURFACE,
                                fg=Theme.active().TXT_ON_SURFACE)
        self.description_label = Label(master=self.frame,
                                       bg=Theme.active().SURFACE,
                                       fg=Theme.active().TXT_ON_SURFACE)

    def render(self):
        self.frame.place(relwidth=1, relheight=self.relheight, relx=0, rely=self.rely)
        self.time_label.place(relx=0.05, rely=0, relheight=1, relwidth=0.25)
        self.description_label.place(relx=0.3, rely=0, relheight=1, relwidth=0.7)
        self.index_label.place(relx=0, rely=0, relheight=1, relwidth=0.05)

    def set_alert(self, alert, index):
        self.time_label.configure(text=alert.date())
        self.description_label.configure(text=str(alert))
        self.index_label.configure(text=str(index))

    def hide(self):
        self.frame.place_forget()
