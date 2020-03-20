import tkinter
tk = tkinter
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import numpy as np


root = Tk()
root.title("Respirator")
root.geometry('800x480')

x = np.arange(0, 3, .01)


debug_running_counter = 0


def exitProgram():
	print("Exit Button pressed")
        # GPIO.cleanup()
	root.quit()

def change_vol_graph_each_time():
	global debug_running_counter
	update_volume_graph(np.sin(x + debug_running_counter))
	debug_running_counter += 1


def change_pres_graph_each_time():
	global debug_running_counter
	update_pressure_graph(np.sin(x + debug_running_counter))
	debug_running_counter += 1

def update_pressure_graph(ydata):
	pressure_y.set_ydata(ydata)
	pressure_graph.canvas.draw()
	pressure_graph.canvas.flush_events()


def update_volume_graph(ydata):
	volume_y.set_ydata(ydata)
	volume_graph.canvas.draw()
	volume_graph.canvas.flush_events()




def prompt_for_confirmation():
	print("Prompting...")


exitButton  = Button(root, text ="Exit", command = exitProgram, height =2, width = 6)
exitButton.pack(side = BOTTOM)

volume_button_frame = tkinter.Frame(root)
volume_increase_threshold_button  = Button(volume_button_frame, text ="+", command = change_vol_graph_each_time, height =2, width = 6)
volume_decrease_threshold_button  = Button(volume_button_frame, text ="-", command = change_vol_graph_each_time, height =2, width = 6)
volume_button_frame.pack(fill=tkinter.X, side=tkinter.BOTTOM)
volume_button_frame.columnconfigure(0, weight=1)
volume_button_frame.columnconfigure(1, weight=1)
volume_increase_threshold_button.grid(row=0, column=0, sticky=tk.W+tk.E)
volume_decrease_threshold_button.grid(row=1, column=0, sticky=tk.W+tk.E)


pressure_button_frame = tkinter.Frame(root)
pressure_increase_threshold_button  = Button(pressure_button_frame, text ="+", command = change_pres_graph_each_time, height =2, width = 6)
pressure_decrease_threshold_button  = Button(pressure_button_frame, text ="-", command = change_pres_graph_each_time, height =2, width = 6)
pressure_button_frame.pack(fill=tkinter.X, side=tkinter.BOTTOM)
pressure_button_frame.columnconfigure(0, weight=1)
pressure_button_frame.columnconfigure(1, weight=1)
pressure_increase_threshold_button.grid(row=0, column=0, sticky=tk.W+tk.E)
pressure_decrease_threshold_button.grid(row=1, column=0, sticky=tk.W+tk.E)


pressure_graph = Figure(figsize=(5, 2), dpi=100)
pressure_axis = pressure_graph.add_subplot(111, label="pressure")
pressure_y, = pressure_axis.plot(x, 2 * np.sin(2 * np.pi * x))

volume_graph = Figure(figsize=(5, 2), dpi=100)
volume_axis = volume_graph.add_subplot(111, label="volume")
volume_y, = volume_axis.plot(x, 2 * np.sin(2 * np.pi * x))

canvas1 = FigureCanvasTkAgg(pressure_graph, master=root)  # A tk.DrawingArea.
canvas2 = FigureCanvasTkAgg(volume_graph, master=root)  # A tk.DrawingArea.
canvas1.draw()
canvas2.draw()
canvas1.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)
canvas2.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

mainloop()
