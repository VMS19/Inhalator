from tkinter import Button, PhotoImage


class ImageButton(Button):
    def __init__(self, image_path=NotImplemented, **kw):
        self._image = PhotoImage(file=image_path)
        super(ImageButton, self).__init__(**kw)
        self.command = self["command"]
        self.bg = self["bg"]
        self.fg = self["fg"]
        self.activebackground = self["activebackground"]
        self.activeforeground = self["activeforeground"]

        self.configure(image=self._image,
                       activeforeground=self.fg,
                       activebackground=self.bg)
        self.bind('<ButtonPress-1>', self.on_press)
        self.bind('<ButtonRelease-1>', self.on_release)

    def on_press(self, event):
        if self["state"] != "disabled":
            self.configure(fg=self.activeforeground,
                           bg=self.activebackground,
                           activeforeground=self.activeforeground,
                           activebackground=self.activebackground)

    def on_release(self, event):
        self.configure(fg=self.fg,
                       bg=self.bg,
                       activebackground=self.bg,
                       activeforeground=self.fg)

    def set_image(self, path):
        self._image = PhotoImage(file=path)
        self.configure(image=self._image)
