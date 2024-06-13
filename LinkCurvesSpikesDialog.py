import tkinter as tk
from tkinter import ttk

from PlotCurve import PALETTE_OBJECT_GRAPH, PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_ENABLED

class LinkCurvesSpikesDialog:
    def __init__(self, curves, curve_names, spikes, spike_names):
        self.curves = curves
        self.curve_names = curve_names
        self.spikes = spikes
        self.spike_names = spike_names

        self.window = tk.Tk()
        self.window.title("Link Curves to Spikes")

        # Curves ComboBox
        self.curve_label = tk.Label(self.window, text="Select Curve:")
        self.curve_label.grid(row=0, column=0, padx=10, pady=10)
        
        self.curve_combobox = ttk.Combobox(self.window, values=self.curve_names)
        self.curve_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.curve_combobox.bind("<<ComboboxSelected>>", self.update_curve_color)

        # Spikes ComboBox
        self.spike_label = tk.Label(self.window, text="Select Spike:")
        self.spike_label.grid(row=1, column=0, padx=10, pady=10)
        
        self.spike_combobox = ttk.Combobox(self.window, values=self.spike_names)
        self.spike_combobox.grid(row=1, column=1, padx=10, pady=10)
        self.spike_combobox.bind("<<ComboboxSelected>>", self.update_spikes_color)

        # Buttons
        self.link_button = tk.Button(self.window, text="Link", command=self.link)
        self.link_button.grid(row=2, column=0, padx=10, pady=10)
        
        self.cancel_button = tk.Button(self.window, text="Cancel", command=self.window.destroy)
        self.cancel_button.grid(row=2, column=1, padx=10, pady=10)

    def update_curve_color(self, event):
        selected_curve_name = self.curve_combobox.get()
        index = self.curve_names.index(selected_curve_name)
        curve = self.curves[index]
        self.curve_combobox.config(foreground=curve.theme.get_color(PALETTE_OBJECT_GRAPH, PALETTE_PROPERTY_PLOT_ENABLED))

    def update_spikes_color(self, event):
        selected_spikes_name = self.spike_combobox.get()
        index = self.spike_names.index(selected_spikes_name)
        spikes = self.spikes[index]
        self.spike_combobox.config(foreground=spikes.theme.get_color(PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_ENABLED))

    def link(self):
        selected_curve = self.curve_combobox.get()
        selected_spike = self.spike_combobox.get()
        print(f"Linked {selected_curve} to {selected_spike}")
        # Perform the actual linking logic here
        self.window.destroy()

    def run(self):
        self.window.mainloop()
