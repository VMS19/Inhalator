import os
from tkinter import Frame

from graphics import RESOURCES_DIRECTORY
from graphics.imagebutton import ImageButton
from graphics.themes import Theme


class ScrollUpDownContainer(object):

    DOWN_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY, "baseline_less_white_36dp.png")
    UP_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY, "baseline_more_white_36dp.png")

    def __init__(self, parent, root):
        self.root = root
        self.parent = parent
        self.frame = Frame(master=self.root, bg=Theme.active().BACKGROUND)

        self.up_button = ImageButton(master=self.frame,
                                     image_path=self.UP_IMAGE_PATH,
                                     compound="center",
                                     command=self.parent.on_scroll_up,
                                     bg=Theme.active().BUTTON,
                                     activebackground=Theme.active().BUTTON_ACTIVE)

        self.down_button = ImageButton(master=self.frame,
                                       image_path=self.DOWN_IMAGE_PATH,
                                       compound="center",
                                       command=self.parent.on_scroll_down,
                                       bg=Theme.active().BUTTON,
                                       activebackground=Theme.active().BUTTON_ACTIVE)

    def render(self):
        self.frame.place(relx=0.85, rely=0, relwidth=0.15, relheight=1)
        self.up_button.place(relx=0, rely=0, relheight=0.5, relwidth=1)
        self.down_button.place(relx=0, rely=0.5, relheight=0.5, relwidth=1)