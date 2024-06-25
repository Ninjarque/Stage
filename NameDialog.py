import tkinter as tk
from tkinter import ttk

from PlotCurve import PALETTE_OBJECT_GRAPH, PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_ENABLED

class NameDialog:
    def __init__(self, title):
        self.window = tk.Tk()
        self.window.title(title)
        self.name = ""

        

    def accept(self):
        # Perform the actual linking logic here
        self.window.destroy()

    def run(self):
        self.window.mainloop()
        return self.name
