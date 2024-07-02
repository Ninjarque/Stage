import os
import matplotlib.pyplot as plt

from PlotCurve import *
from lod_manager import *

from JsonComponent import JsonComponent

class CanvasSpikes:
    def __init__(self, file_path, ax, spikes_data, x_data, color_palette, linestyle='-'):
        self.ax = ax
        self.linestyle = linestyle
        self.spikes = []
        self.spikes_data = spikes_data
        self.spikes_data.sort(key=lambda spike: spike.x)

        self.file_path = file_path

        filename, file_extension = os.path.splitext(file_path)
        self.name = filename.split("\\")[-1].split("/")[-1]
        print("Curve name '", self.name, "'")
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
        dx, self.displayed_data = self.lod.get_compressed_data(self.x_data, self.spikes_data)

        self.spike_mapping = {}  # Add this line

        self.create_spikes(dx)

    def clear(self):
        self.clear_spikes()

    def to_json_component(self):
        properties = {
            "file_path": self.file_path,
            "theme": self.color_palette.to_dict()
        }
        return JsonComponent("CanvasSpikes", properties)

    @staticmethod
    def from_json_component(component, plot):
        file_path = component.properties.get("file_path", "")

        bars = None
        xdata = None
        filename, file_extension = os.path.splitext(file_path)
        print("File '", filename, "' is '", file_extension, "' format!")
        if "t" in file_extension.lower():
            bars = loader.parse_T(file_path)
            xdata = [b.x for b in bars]
        if "asg" in file_extension.lower():
            bars = loader.parse_ASG(file_path)
            xdata = [b.x for b in bars]


        color_palette = ColorPalette.from_dict(component.properties.get("theme", {}))
        return CanvasSpikes(file_path, plot, bars, xdata, color_palette)

    def get_file_path(self):
        return self.file_path

    def update_file_path(self, new_path):
        self.file_path = new_path

    def create_spikes(self, x_data):
        self.clear_spikes()  # Clear existing spikes first
        color = self.color_palette.get_color(PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_ENABLED)
        if not self.enabled:
            color = self.color_palette.get_color(PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_DISABLED)

        x_data.sort()
        for x in x_data:
            line = self.ax.axvline(x=x, color=color, linestyle=self.linestyle)
            line.set_zorder(10)
            self.spikes.append(line)
            self.spike_mapping[x] = line  # Update the mapping

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
            # return CODE_NONE

        if not self.enabled:
            needs_redraw = False
            if self.selected_lines != []:
                needs_redraw = True
                self.selected_lines = []
            if self.hovered_lines != []:
                needs_redraw = True
                self.hovered_lines = []
            if needs_redraw:
                self.draw()
            return CODE_NONE

        rcode = CODE_NONE

        if not axes:
            if self.hovered_lines:
                self.hovered_lines = []
                self.draw()
        if axes:
            closest_lines = self.get_closest_lines(posx, posy)
            needs_redraw = False
            if self.hovered_lines:
                needs_redraw = True
            if self.hovered_lines != closest_lines:
                rcode = CODE_HOVERED_LINE
            self.hovered_lines = closest_lines
            if self.hovered_lines:
                rcode = CODE_HOVERED_LINE
                needs_redraw = True
            if needs_redraw:
                self.draw()

            if self.hovered_lines and click_released and not moved_too_much:
                self.selected_lines = self.hovered_lines
                selected_spikes = self.lines_to_spikes(self.selected_lines)
                for spike in selected_spikes:
                    print("The closest spike to current selection is:", spike.id)
                self.draw()
                #lines are getting cleared upon move, further testing will be required

        return rcode
    
    def lines_to_spikes(self, lines):
        selected_spikes = []
        for line in self.selected_lines:
            x = line.get_xdata()[0]
            spikes_range = dichotomy.nearest_indexes(x, self.x_data, len(lines))
            data = self.spikes_data[spikes_range[0]:spikes_range[1] + 1]
            for spike in data:
                if x == spike.x and not spike in selected_spikes:
                    selected_spikes.append(spike)
        return selected_spikes
    
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
        if posx is None or posy is None:
            return closest_lines

        dists_lst = []
        line_hover_precision = 0.01
        for bar in self.displayed_data:
            line = self.spike_mapping.get(bar.x)  # Use the mapping
            if line:
                dist = abs(bar.x - posx)
                if dist < line_hover_precision * self.x_range:  # Threshold to select a line
                    dists_lst.append((dist, line))

        if not dists_lst:
            return []

        # Sort by distance
        dists_lst.sort(key=lambda x: x[0])
        closest_lines = [line for _, line in dists_lst]

        return closest_lines

    def set_color(self, color):
        for line in self.spikes:
            line.set_color(color)
        
    def link_graph(self, graph):
        self.linked_graph = graph
        if graph:
            graph.link_plotbar(self)
            self.lod = LODBarManager(graph.plot, len(self.x_data), self.max_bars_rendered)
            dx, self.displayed_data = self.lod.get_compressed_data(self.x_data, self.spikes_data)
            self.update_spikes(dx)

    def enable(self):
        self.enabled = True
        #self.create_spikes(self.x_data)
        self.set_color(self.color_palette.get_color(PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_ENABLED))
    def disable(self):
        self.enabled = False
        #self.clear_spikes()
        self.set_color(self.color_palette.get_color(PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_DISABLED))

    def apply_color_palette(self):
        for line in self.spikes:
            if not self.enabled:
                line.set_color(self.color_palette.get_color(PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_DISABLED))
                continue
            if line in self.selected_lines:
                line.set_color(self.color_palette.get_color(PALETTE_OBJECT_BAR, PALETTE_PROPERTY_LINE_SELECTED))
            elif line in self.hovered_lines:
                line.set_color(self.color_palette.get_color(PALETTE_OBJECT_BAR, PALETTE_PROPERTY_LINE_HOVERED))
            else:
                line.set_color(self.color_palette.get_color(PALETTE_OBJECT_BAR, PALETTE_PROPERTY_PLOT_ENABLED))



    def draw(self):
        if self.lod.update():
            dx, self.displayed_data = self.lod.get_compressed_data(self.x_data, self.spikes_data)
            self.update_spikes(dx)
        self.apply_color_palette()
        pass