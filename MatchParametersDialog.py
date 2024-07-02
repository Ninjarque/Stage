import tkinter as tk
from tkinter import ttk

from PlotCurve import PALETTE_OBJECT_GRAPH, PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_ENABLED

class MatchParametersDialog:
    def __init__(self, project):
        self.project = project
        self.curves = project.curves
        self.target_names = [curve.name for curve in self.curves]
        self.current_names = [curve.name for curve in self.curves]
        self.window = tk.Toplevel()
        self.window.title("Matching parameters")

        # Curves ComboBox
        self.target_label = tk.Label(self.window, text="Select Target Curve:")
        self.target_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.target_combobox = ttk.Combobox(self.window, values=self.target_names)
        self.target_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.target_combobox.bind("<<ComboboxSelected>>", self.update_target_color)
        if self.project.target_curve != "" and self.project.target_curve in self.target_names:
            self.target_combobox.current(self.target_names.index(self.project.target_curve))

        # Spikes ComboBox
        self.current_label = tk.Label(self.window, text="Select Current Curve:")
        self.current_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.current_combobox = ttk.Combobox(self.window, values=self.current_names)
        self.current_combobox.grid(row=1, column=1, padx=10, pady=10)
        self.current_combobox.bind("<<ComboboxSelected>>", self.update_current_color)
        if self.project.current_curve != "" and self.project.current_curve in self.current_names:
            self.current_combobox.current(self.current_names.index(self.project.current_curve))

        # Buttons
        self.match_button = tk.Button(self.window, text="Match", command=self.match)
        self.match_button.grid(row=2, column=0, padx=10, pady=10)
        
        self.cancel_button = tk.Button(self.window, text="Cancel", command=self.window.destroy)
        self.cancel_button.grid(row=2, column=1, padx=10, pady=10)

        self.validated = False

    def update_target_color(self, event):
        selected_name = self.target_combobox.get()
        index = self.target_names.index(selected_name)
        curve = self.curves[index]
        self.target_combobox.config(foreground=curve.color_palette.get_color(PALETTE_OBJECT_GRAPH, PALETTE_PROPERTY_PLOT_ENABLED))

    def update_current_color(self, event):
        selected_name = self.current_combobox.get()
        index = self.current_names.index(selected_name)
        curve = self.curves[index]
        self.current_combobox.config(foreground=curve.color_palette.get_color(PALETTE_OBJECT_GRAPH, PALETTE_PROPERTY_PLOT_ENABLED))

    def match(self):
        target_curve = self.target_combobox.get()
        current_curve = self.current_combobox.get()
        print(f"Assigned {target_curve} as target and {current_curve} as current curve")
        self.project.target_curve = target_curve
        self.project.current_curve = current_curve
        self.validated = True
        self.window.destroy()

    def run(self):
        self.window.grab_set()  # Make the dialog modal
        self.window.wait_window()  # Wait until the dialog is closed
