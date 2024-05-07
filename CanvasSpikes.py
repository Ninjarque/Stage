import matplotlib.pyplot as plt

from plot import *
from lod_manager import *

class CanvasSpikes:
    def __init__(self, ax, x_data, color_palette, linestyle='-'):
        self.ax = ax
        self.linestyle = linestyle
        self.spikes = []

        self.linked_graph = None

        self.enabled = True

        # Colors
        self.color_palette = color_palette

        self.max_bars_rendered = 75

        x_data.sort()
        self.x_data = x_data
        self.lod = LODBarManager(self.ax, len(self.x_data), self.max_bars_rendered)
        dx = self.lod.get_compressed_data(self.x_data)

        self.create_spikes(dx)


    def create_spikes(self, x_data):
        # Clear existing lines if any
        for line in self.spikes:
            line.remove()
        self.spikes = []

        color = self.color_palette.get_color(PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_ENABLED)
        if not self.enabled:
            color = self.color_palette.get_color(PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_DISABLED)

        # Create new lines
        x_data.sort()
        for x in x_data:
            line = self.ax.axvline(x=x, color=color, linestyle=self.linestyle)
            self.spikes.append(line)

    def update_spikes(self, x_data):
        if len(x_data) != len(self.spikes):
            # If the number of spikes has changed, recreate them
            self.create_spikes(x_data)
        else:
            x_data.sort()
            # Otherwise, just update their positions
            for line, x in zip(self.spikes, x_data):
                line.set_xdata([x, x])

    def clear_spikes(self):
        for line in self.spikes:
            line.remove()
        self.spikes = []

    def set_color(self, color):
        for line in self.spikes:
            line.set_color(color)
        
    def link_graph(self, graph):
        self.linked_graph = graph
        if graph:
            graph.link_plotbar(self)
            self.lod = LODBarManager(graph.plot, len(self.x_data), self.max_bars_rendered)
            dx = self.lod.get_compressed_data(self.x_data)
            self.update_spikes(dx)

    def enable(self):
        self.enabled = True
        #self.create_spikes(self.x_data)
        self.set_color(self.color_palette.get_color(PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_ENABLED))
    def disable(self):
        self.enabled = False
        #self.clear_spikes()
        self.set_color(self.color_palette.get_color(PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_DISABLED))

    def draw(self):
        if self.lod.update():
            dx = self.lod.get_compressed_data(self.x_data)
            self.update_spikes(dx)
        pass