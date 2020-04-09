from tkinter import Frame, Label

from graphics.themes import Theme


class AlertTitles(object):
    def __init__(self, root):
        self.root = root
        self.frame = Frame(master=self.root)
        self.index_label = Label(master=self.frame,
                                text="",
                                font=("Roboto", 20),
                                bg=Theme.active().BACKGROUND,
                                fg=Theme.active().TXT_ON_BG)

        self.time_label = Label(master=self.frame,
                                text="Date",
                                font=("Roboto", 20),
                                bg=Theme.active().BACKGROUND,
                                fg=Theme.active().TXT_ON_BG)

        self.description_label = Label(master=self.frame,
                                       text="Description",
                                       font=("Roboto", 20),
                                       bg=Theme.active().BACKGROUND,
                                       fg=Theme.active().TXT_ON_BG)

    def render(self):
        self.frame.place(relx=0, rely=0, relwidth=0.85, relheight=0.15)
        self.index_label.place(relx=0, rely=0, relheight=1, relwidth=0.05)
        self.time_label.place(relx=0.05, rely=0, relheight=1, relwidth=0.3)
        self.description_label.place(relx=0.35, rely=0, relheight=1, relwidth=0.65)