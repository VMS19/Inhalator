import tkinter
from tkinter import *
# import tkFont
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np

# import RPi.GPIO as GPIO

# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(40, GPIO.OUT)
# GPIO.output(40, GPIO.LOW)

win = Tk()

# myFont = tkFont.Font(family = 'Helvetica', size = 36, weight = 'bold')


def exitProgram():
	print("Exit Button pressed")
        # GPIO.cleanup()
	win.quit()	


win.title("First GUI")
win.geometry('800x480')

exitButton  = Button(win, text = "Exit", command = exitProgram, height =2 , width = 6)
exitButton.pack(side = BOTTOM)

pressure_graph = Figure(figsize=(5, 2), dpi=100)
volume_graph = Figure(figsize=(5, 2), dpi=100)
t = np.arange(0, 3, .01)
pressure_graph.add_subplot(111, label="pressure").plot(t, 2 * np.sin(2 * np.pi * t))
volume_graph.add_subplot(111, label="volume").plot(t, 2 * np.sin(2 * np.pi * t))

canvas1 = FigureCanvasTkAgg(pressure_graph, master=win)  # A tk.DrawingArea.
canvas2 = FigureCanvasTkAgg(volume_graph, master=win)  # A tk.DrawingArea.
canvas1.draw()
canvas2.draw()
canvas1.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
canvas2.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

mainloop()
