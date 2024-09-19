import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class ThresholdDialog:
    def __init__(self, project, curve):
        self.project = project
        self.curve = curve
        self.threshold_value = 0.5  # Default threshold

        # Create the dialog window
        self.window = tk.Toplevel()
        self.window.title("Set Threshold for Curve")

        # Set up a Matplotlib figure and canvas
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title(f"Threshold for {self.curve.name}")

        # Plot the curve initially
        self.plot_curve()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0)

        # Add a vertical threshold slider
        self.slider_label = tk.Label(self.window, text="Threshold:")
        self.slider_label.grid(row=0, column=1, padx=10, pady=10)

        self.slider = ttk.Scale(self.window, from_=1, to=0, orient="vertical", command=self.on_threshold_change)
        self.slider.set(self.threshold_value)
        self.slider.grid(row=0, column=2, padx=10, pady=10)

        # Buttons
        self.ok_button = tk.Button(self.window, text="OK", command=self.on_ok)
        self.ok_button.grid(row=1, column=0, padx=10, pady=10)

        self.cancel_button = tk.Button(self.window, text="Cancel", command=self.window.destroy)
        self.cancel_button.grid(row=1, column=2, padx=10, pady=10)

        self.validated = False

    def plot_curve(self):
        """
        Plot the curve and highlight clusters above the threshold.
        """
        # Clear the plot
        self.ax.clear()

        # Get the clusters from the curve
        clusters = self.curve.spikes_clusters

        # Plot the entire curve
        for cluster in clusters:
            self.ax.plot(cluster.spikesX, cluster.spikesY, color='lightblue')

        # Highlight clusters where any spikeY value exceeds the threshold
        threshold = self.threshold_value
        for cluster in clusters:
            if max(cluster.spikesY) > threshold:
                self.ax.plot(cluster.spikesX, cluster.spikesY, color='red', linewidth=2)

        # Add a horizontal line representing the threshold
        self.ax.axhline(y=threshold, color='green', linestyle='--', label=f'Threshold: {threshold}')

        # Redraw the canvas with the updated plot
        self.canvas.draw()

    def on_threshold_change(self, value):
        """
        Update the threshold value and re-plot the curve to reflect the changes.
        """
        self.threshold_value = float(value)
        self.plot_curve()

    def on_ok(self):
        """
        Set the threshold value and close the dialog.
        """
        self.curve.threshold = self.threshold_value  # Store the threshold in the curve object
        self.validated = True
        self.window.destroy()

    def run(self):
        self.window.grab_set()  # Make the dialog modal
        self.window.wait_window()  # Wait until the dialog is closed