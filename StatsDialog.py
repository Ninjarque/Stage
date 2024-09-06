import tkinter as tk
from tkinter import ttk

from PlotCurve import PALETTE_OBJECT_GRAPH, PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_ENABLED

import dichotomy

from FeatureExtractor import *

from CurveDistanceCalculator import *

class StatsDialog:
    def __init__(self, project):
        self.project = project
        self.curves = project.curves
        self.target_names = [curve.name for curve in self.curves]
        self.current_names = [curve.name for curve in self.curves]


        #self.window = tk.Toplevel()
        #self.window.title("Statistics display")

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
        current_curve = project.curves[current_plot_index]

        target_curve_datax = target_curve.full_datax
        target_curve_datay = target_curve.full_datay

        current_curve_datax = current_curve.full_datax
        current_curve_datay = current_curve.full_datay

        RMSE = CurveDistanceCalculator.calculate_rmse(target_curve_datax, target_curve_datay, current_curve_datax, current_curve_datay)


        print("RMSE:", RMSE)
        ##self.RMSE_label = tk.Label(self.window, text=str(RMSE))

    def run(self):
        return
        #self.window.grab_set()  # Make the dialog modal
        #self.window.wait_window()  # Wait until the dialog is closed
