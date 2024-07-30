import tkinter as tk
from tkinter import ttk

from PlotCurve import PALETTE_OBJECT_GRAPH, PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_ENABLED

import dichotomy

from FeatureExtractor import *

class StatsDialog:
    def __init__(self, project):
        self.project = project
        self.curves = project.curves
        self.target_names = [curve.name for curve in self.curves]
        self.current_names = [curve.name for curve in self.curves]


        self.window = tk.Toplevel()
        self.window.title("Statistics display")

        return

        RMSE = 0

        curve_names = [curve.name for curve in project.curves]

        target_plot_index = 0
        current_plot_index = 0

        if project.target_curve != "" and project.target_curve in curve_names:
            target_plot_index = curve_names.index(project.target_curve)
        else:
            print("Didn't have a proper target curve, exiting match operation...")
            return
        if project.current_curve != "" and project.current_curve in curve_names:
            current_plot_index = curve_names.index(project.current_curve)
        else:
            print("Didn't have a proper current curve, exiting match operation...")
            return
        
        target_curve = project.curves[target_plot_index]
        current_curve = project.curves[target_plot_index]

        target_curve_datax = target_curve.full_datax
        target_curve_datay = target_curve.full_datay

        current_curve_datax = current_curve.full_datax
        current_curve_datay = current_curve.full_datay

        if target_curve_datax[0] < current_curve_datax[0]:
            i = dichotomy.nearest_index(current_curve_datax[0], target_curve_datax)
            target_curve_datax = target_curve_datax[i:-1]
            target_curve_datay = target_curve_datay[i:-1]
        else:
            i = dichotomy.nearest_index(target_curve_datax[0], current_curve_datax)
            current_curve_datax = current_curve_datax[i:-1]
            current_curve_datay = current_curve_datay[i:-1]
        if target_curve_datax[-1] > current_curve_datax[-1]:
            i = dichotomy.nearest_index(current_curve_datax[0], target_curve_datax)
            target_curve_datax = target_curve_datax[0:i]
            target_curve_datay = target_curve_datay[0:i]
        else:
            i = dichotomy.nearest_index(target_curve_datax[0], current_curve_datax)
            current_curve_datax = current_curve_datax[0:i]
            current_curve_datay = current_curve_datay[0:i]

        feature = DistanceFeatureExtractor([1])
        RMSE = feature.distance(target_curve_datax, target_curve_datay, current_curve_datax, current_curve_datay, None, None)

        print(RMSE)
        self.RMSE_label = tk.Label(self.window, text=str(RMSE))


        '''
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
        '''
        
        self.cancel_button = tk.Button(self.window, text="OK", command=self.window.destroy)
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
