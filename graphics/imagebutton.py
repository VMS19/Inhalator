from tkinter import Button, PhotoImage


class ImageButton(Button):
    def __init__(self, image_path=NotImplemented, **kw):
        self._image = PhotoImage(file=image_path)
        super(ImageButton, self).__init__(**kw)
        self.configure(image=self._image)

    def set_image(self, path):
        self._image = PhotoImage(file=path)
        self.configure(image=self._image)
