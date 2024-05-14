import matplotlib.pyplot as plt

from plot import *
from lod_manager import *

class CanvasSpikes:
    def __init__(self, ax, spikes_data, x_data, color_palette, linestyle='-'):
        self.ax = ax
        self.linestyle = linestyle
        self.spikes = []
        self.spikes_data = spikes_data
        self.displayed_spikes = spikes_data

        self.linked_graph = None

        self.enabled = True

        # Colors
        self.color_palette = color_palette

        # Limits
        self.x_lims = self.ax.get_xlim()
        self.y_lims = self.ax.get_ylim()
        self.x_range = abs(self.x_lims[1] - self.x_lims[0])
        self.y_range = abs(self.y_lims[1] - self.y_lims[0])

        # Selection
        self.hovered_lines = []
        self.selected_lines = []

        self.max_bars_rendered = 75

        x_data.sort()
        self.x_data = x_data
        self.lod = LODBarManager(self.ax, len(self.x_data), self.max_bars_rendered)
        self.displayed_spikes, dx = self.lod.get_compressed_data(self.spikes_data, self.x_data)

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
            line.set_zorder(10)
            line.set_visible(True)
            self.spikes.append(line)

    def update_spikes(self, x_data):
        '''
        if len(x_data) != len(self.spikes):
            # If the number of spikes has changed, recreate them
            self.create_spikes(x_data)
        else:
            x_data.sort()
            # Otherwise, just update their positions
            for line, x in zip(self.spikes, x_data):
                line.set_xdata([x, x])
                line.set_zorder(10)
                line.set_visible(True)
        self.ax.relim()  # Recalculate limits
        self.ax.autoscale_view()  # Auto-scale view based on limits
        '''
            # Assuming that spikes need to be updated completely every time
        self.clear_spikes()  # Remove old spikes first
        self.create_spikes(x_data)  # Create new spikes
        self.ax.figure.canvas.draw()  # Redraw the canvas to update the view


    def clear_spikes(self):
        for line in self.spikes:
            line.remove()
        self.spikes = []

    def update_mouse(self, axes, posx, posy, moved_too_much, click_pressed, click_released):
        if axes != self.ax:
            axes = None

        rcode = CODE_NONE

        if not self.selected_lines and axes:
            closest_lines = self.get_closest_lines(posx, posy)
            if self.hovered_lines:
                for i in self.hovered_lines:
                    line = self.spikes[i]
                    line.set_color("black")

                pass
            if self.hovered_lines != closest_lines:
                rcode = CODE_HOVERED_LINE
            self.hovered_lines = closest_lines
            if self.hovered_lines:
                rcode = CODE_HOVERED_LINE
                for i in self.hovered_lines:
                    line = self.spikes[i]
                    line.set_color("yellow")
                pass
            else:
                self.draw()

        return rcode
    
    def update_key(self, key, pressed, released):
        if not self.enabled:
            return CODE_NONE
        if key == 'x':
            pass
        
        return CODE_NONE
    
    def update_limits(self, limits_xmin, limits_xmax, limits_ymin, limits_ymax):
        self.x_range = abs(limits_xmax - limits_xmin)
        self.y_range = abs(limits_ymax - limits_ymin)
        return CODE_NONE

    def get_closest_lines(self, posx, posy):
        closest_lines = []
        if not posx or not posy:
            return closest_lines
        dists_lst = []
        index_lst = []

        line_hover_precision = 0.02

        '''
        for i in range(len(self.displayed_spikes)):
            bar = self.displayed_spikes[i]
            dist = abs(bar.x - posx)
            if dist < line_hover_precision * self.x_range:  # Threshold to select a line
                curr_dist = None
                index_lst = 0
                if len(dists_lst) != 0:
                    curr_dist = dists_lst[0]
                while index_lst < len(dists_lst) and curr_dist < dist:
                    curr_dist = dists_lst[index_lst]
                    index_lst += 1
                dists_lst.insert(index_lst, dist)
                closest_lines.insert(index_lst, i)
        '''

        for i, bar in enumerate(self.displayed_spikes):
            dist = abs(bar.x - posx)
            if dist < line_hover_precision * self.x_range:  # Threshold to select a line
                dists_lst.append(dist)
                closest_lines.append(i)

        if not closest_lines:
            return []
        
        # Combine the lists, sort by distance, and separate them again
        combined = sorted(zip(dists_lst, closest_lines))
        dists_lst, closest_lines = zip(*combined)  # This will sort dists_lst and reorder closest_lines accordingly

        print(dists_lst)
        print(closest_lines)
        return closest_lines

    def set_color(self, color):
        for line in self.spikes:
            line.set_color(color)
        
    def link_graph(self, graph):
        self.linked_graph = graph
        if graph:
            graph.link_plotbar(self)
            self.lod = LODBarManager(graph.plot, len(self.x_data), self.max_bars_rendered)
            self.displayed_spikes, dx = self.lod.get_compressed_data(self.spikes_data, self.x_data)
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
            self.displayed_spikes, dx = self.lod.get_compressed_data(self.spikes_data, self.x_data)
            self.update_spikes(dx)
        pass