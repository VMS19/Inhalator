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

    @property
    def textual(self):
        return self.index_label, self.time_label, self.description_label

    @property
    def with_background(self):
        return self.index_label, self.description_label, self.time_label, self.frame

    def set_unseen(self):
        for widget in self.with_background:
            widget.configure(bg=Theme.active().UNSEEN_ALERT)

        for widget in self.textual:
            widget.configure(fg=Theme.active().TXT_ON_UNSEEN_ALERT)

    def set_seen(self):
        for widget in self.with_background:
            widget.configure(bg=Theme.active().SURFACE)

        for widget in self.textual:
            widget.configure(fg=Theme.active().TXT_ON_SURFACE)

    def render(self):
        self.frame.place(relwidth=1, relheight=self.relheight, relx=0, rely=self.rely)
        self.time_label.place(relx=0.05, rely=0, relheight=1, relwidth=0.30)
        self.description_label.place(relx=0.35, rely=0, relheight=1, relwidth=0.65)
        self.index_label.place(relx=0, rely=0, relheight=1, relwidth=0.05)

    def set_alert(self, alert, index):
        self.time_label.configure(text=alert.date())
        self.description_label.configure(text=str(alert))
        self.index_label.configure(text=str(index))

        if alert.seen:
            self.set_seen()

        else:
            self.set_unseen()

    def hide(self):
        self.frame.place_forget()
