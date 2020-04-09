import os
from tkinter import Frame

from graphics import RESOURCES_DIRECTORY
from graphics.imagebutton import ImageButton
from graphics.themes import Theme


class RightSideMenuContainer(object):

    DOWN_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY, "baseline_less_white_36dp.png")
    UP_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY, "baseline_more_white_36dp.png")
    REFRESH_WHITE_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY, "baseline_refresh_white_36dp.png")
    REFRESH_BLACK_IMAGE_PATH = os.path.join(RESOURCES_DIRECTORY, "baseline_refresh_black_36dp.png")


    def __init__(self, parent, root):
        self.root = root
        self.parent = parent
        self.frame = Frame(master=self.root, bg=Theme.active().BACKGROUND)

        self.up_button = ImageButton(master=self.frame,
                                     image_path=self.UP_IMAGE_PATH,
                                     compound="center",
                                     repeatdelay=500, repeatinterval=100,
                                     command=self.parent.on_scroll_up,
                                     bg=Theme.active().BUTTON,
                                     activebackground=Theme.active().BUTTON_ACTIVE)

        self.down_button = ImageButton(master=self.frame,
                                       image_path=self.DOWN_IMAGE_PATH,
                                       compound="center",
                                       repeatdelay=500, repeatinterval=100,
                                       command=self.parent.on_scroll_down,
                                       bg=Theme.active().BUTTON,
                                       activebackground=Theme.active().BUTTON_ACTIVE)

        self.refresh_button = ImageButton(master=self.frame,
                                          image_path=self.REFRESH_WHITE_IMAGE_PATH,
                                          compound="center",
                                          state="disabled",
                                          command=self.on_refresh_button_click,
                                          bg=Theme.active().BUTTON,
                                          activebackground=Theme.active().BUTTON_ACTIVE)

    def mark_as_needs_refresh(self):
        self.refresh_button["state"] = "active"
        self.refresh_button.configure(bg=Theme.active().REFRESH_BUTTON_ACTIVE_BG,
                                      activebackground=Theme.active().REFRESH_BUTTON_ACTIVE_BG)
        self.refresh_button.set_image(path=self.REFRESH_BLACK_IMAGE_PATH)

    def on_refresh_button_click(self):
        self.refresh_button["state"] = "disabled"
        self.refresh_button.configure(bg=Theme.active().BUTTON)
        self.refresh_button.set_image(path=self.REFRESH_WHITE_IMAGE_PATH)
        self.parent.on_refresh_button_click()

    def render(self):
        self.frame.place(relx=0.85, rely=0, relwidth=0.15, relheight=1)
        self.up_button.place(relx=0, rely=0, relheight=(1/3), relwidth=1)
        self.down_button.place(relx=0, rely=(1/3), relheight=(1/3), relwidth=1)
        self.refresh_button.place(relx=0, rely=(2/3), relheight=(1/3), relwidth=1)