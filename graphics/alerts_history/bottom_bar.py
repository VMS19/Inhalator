import os
from tkinter import Frame

from graphics import RESOURCES_DIRECTORY
from graphics.imagebutton import ImageButton
from graphics.themes import Theme


class BottomBar(object):
    BACK_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY, "baseline_exit_to_app_white_24dp.png")

    def __init__(self, parent, root):
        self.parent = parent
        self.root = root
        self.frame = Frame(master=self.root, bg=Theme.active().BACKGROUND)
        self.back_btn = ImageButton(master=self.frame,
                               bg=Theme.active().RIGHT_SIDE_BUTTON_BG,
                               image_path=self.BACK_IMAGE_PATH,
                               font=("Roboto", 20),
                               command=self.on_click,
                               fg=Theme.active().RIGHT_SIDE_BUTTON_FG,
                               activebackground=Theme.active().RIGHT_SIDE_BUTTON_BG_ACTIVE,
                               activeforeground=Theme.active().RIGHT_SIDE_BUTTON_FG_ACTIVE)

    def on_click(self):
        self.parent.on_back_button_click()

    def render(self):
        self.frame.place(relx=0, rely=0.85, relwidth=0.85, relheight=0.15)
        self.back_btn.place(relx=0.25, rely=0.1, relheight=0.8, relwidth=0.5)