import math
from matplotlib.figure import Figure 
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,  
NavigationToolbar2Tk) 
import matplotlib.transforms as transforms
import numpy as np

import loader
from theme import *
from lod_manager import *

CODE_NONE = 0
CODE_ADDING_LINE = 1
CODE_REMOVING_LINE = 2

CODE_SELECTED_LINE = 10
CODE_UNSELECTED_LINE = 11
CODE_HOVERED_LINE = 12


CODE_HOVERED_PLOT = 20
CODE_SELECTED_PLOT = 21


RANGE_MODE_FULL = 0
RANGE_MODE_CLUSTERS = 1

CURVE_Z_SEPARATION = 10


PLOT_MOUSE_INDEXES_DISTANCE_CHECKS = 400
PLOT_MOUSE_DISTANCE_THRESHOLD = 0.02


PALETTE_OBJECT_BAR = "bar"
PALETTE_OBJECT_GRAPH = "graph"
PALETTE_OBJECT_GRAPH_SELECTION = "selection"
PALETTE_OBJECT_LINE = "line"



PALETTE_PROPERTY_PLOT_ENABLED = "enabled"
PALETTE_PROPERTY_PLOT_DISABLED = "disabled"
PALETTE_PROPERTY_PLOT_HOVERED = "hovered"

PALETTE_PROPERTY_LINE_ENABLED = "enabled"
PALETTE_PROPERTY_LINE_DISABLED = "disabled"
PALETTE_PROPERTY_LINE_HOVERED = "hovered"
PALETTE_PROPERTY_LINE_SELECTED = "selected"

class PlotCurve:
    def __init__(self, plot, spikes_clusters, 
                 line_hover_precision,
                 color_palette,
                 range_mode):
        # Graph
        self.plot = plot

        # Data
        self.spikes_clusters = spikes_clusters

        datax, datay = loader.graph_DPT(spikes_clusters)
        self.graph = self.plot.plot(datax, datay, color='lightblue')[0]
        self.graph_selections = self.plot.plot([], [], color='orange', linewidth=2, zorder=5)[0]

        self.datax, self.datay = self.graph.get_data()

        self.lod = LODCurveManager(self.plot, len(self.datax), 1000)
        dx, dy = self.lod.get_compressed_data(self.datax, self.datay)
        self.set_data(dx, dy)

        # Lines management
        self.number_lines = 0
        self.next_line_id = 0
        self.lines = {}
        self.selected_line = None
        self.hovered_line = None
        self.line_hover_precision = line_hover_precision

        # Ranges
        self.ranges = []
        # Range compute
        self.range_mode = range_mode
        self.needs_recalculate_ranges = True

        # Colors
        self.color_palette = color_palette

        # Limits
        self.x_lims = self.plot.get_xlim()
        self.y_lims = self.plot.get_ylim()
        self.x_range = abs(self.x_lims[1] - self.x_lims[0])
        self.y_range = abs(self.y_lims[1] - self.y_lims[0])

        # Links
        self.plot_bars = []

        self.enabled = True
        self.hovered = False
        self.allow_dragging = True
        self.dragging_plot = False

        self.offset = 0

        self.apply_color_palette()

    def set_data(self, datax, datay):
        self.graph.set_data(datax, datay)
    def set_selection_data(self, datax, datay):
        self.graph_selections.set_data(datax, datay)


    def set_ranges(self, ranges):
        self.ranges = ranges
        self.draw()
        pass

    def set_xoffset(self, offset):
        # Create a transformation that moves the data vertically
        trans = transforms.Affine2D().translate(0, offset) + self.plot.transData

        # Apply the transformation to the line
        self.graph.set_transform(trans)
        self.graph_selections.set_transform(trans)
        self.offset = offset

    def set_zorder(self, offset):
        self.graph.set_zorder(CURVE_Z_SEPARATION * offset)
        self.graph_selections.set_zorder(5 + CURVE_Z_SEPARATION * offset)

    def set_color_palette(self, palette):
        self.color_palette = palette
        self.apply_color_palette()

    def link_plotbar(self, plotbar):
        if plotbar in self.plot_bars:
            return
        self.plot_bars.append(plotbar)
        plotbar.link_graph(self)

    def enable(self):
        self.enabled = True
        self.draw()
    def disable(self):
        self.enabled = False
        self.draw()

    def update_mouse(self, axes, posx, posy, moved_too_much, click_pressed, click_released):
        if axes and not self.selected_line and not self.hovered_line:
            mouse_dist = self.get_distance_to_curve(posx, posy)
            #print(mouse_dist)
            if mouse_dist < PLOT_MOUSE_DISTANCE_THRESHOLD:
                self.hovered = True
                self.draw()
                if click_pressed:
                    if self.allow_dragging:
                        self.dragging_plot = True
                    return CODE_SELECTED_PLOT
                if click_released:
                    self.dragging_plot = False
                return CODE_HOVERED_PLOT
            if self.allow_dragging and self.dragging_plot and not click_released:
                self.set_xoffset(posy)
                #print("dragging...")
                return CODE_SELECTED_PLOT
        if self.hovered:
            self.hovered = False
            self.dragging_plot = False
            self.draw()
            return CODE_HOVERED_PLOT
        if not self.enabled:
            #if click_released or click_released:
            #    self.draw()
            return CODE_NONE
        if axes and not moved_too_much and click_released and not self.hovered_line:
            self.add_line(axes, posx, posy)
            return CODE_ADDING_LINE
        
        rcode = CODE_NONE
        if click_released and self.selected_line:
            preSel = self.selected_line
            self.selected_line = None
            self.update_line_data(preSel, posx, posy)
            rcode = CODE_UNSELECTED_LINE
        
        if not self.selected_line and axes:
            closest_line = self.get_closest_line(posx, posy)
            if self.hovered_line:
                _, line = self.hovered_line
                self.update_line_data(self.hovered_line, None, None)
            if self.hovered_line != closest_line:
                rcode = CODE_HOVERED_LINE
            self.hovered_line = closest_line
            if self.hovered_line:
                _, line = self.hovered_line
                self.update_line_data(self.hovered_line, None, None)
                rcode = CODE_HOVERED_LINE
            else:
                self.draw()

            if click_pressed and self.hovered_line:
                self.selected_line = self.hovered_line
                rcode = CODE_SELECTED_LINE
        
        if self.selected_line:
            self.update_line_data(self.selected_line, posx, posy)
            rcode = CODE_SELECTED_LINE
            
        return rcode

    def update_key(self, key, pressed, released):
        if not self.enabled:
            return CODE_NONE
        if key == 'x':
            if self.hovered_line:
                self.delete_line(self.hovered_line)
                return CODE_REMOVING_LINE
            elif self.selected_line:
                self.delete_line(self.selected_line)
                return CODE_REMOVING_LINE
        
        return CODE_NONE
    
    def update_limits(self, limits_xmin, limits_xmax, limits_ymin, limits_ymax):
        self.x_range = abs(limits_xmax - limits_xmin)
        self.y_range = abs(limits_ymax - limits_ymin)
        return CODE_NONE

    def add_line(self, axes, posx, posy):
        line = axes.axvline(x=posx, color=self.color_palette.get_color(PALETTE_OBJECT_LINE, PALETTE_PROPERTY_LINE_SELECTED), linestyle='--')
        line_id = self.next_line_id  # Unique identifier for the line
        self.lines[line_id] = (line_id, (posx, line))
        if self.number_lines % 2 == 1:  # Assuming ranges are formed between pairs of lines
            last_line_id, (last_xdata, last_line) = self.last_line
            self.ranges.append(SelectionRange(last_line_id, last_xdata, line_id, posx))
            self.needs_recalculate_ranges = True
        self.draw()
        self.last_line = (line_id, (posx, line))
        self.number_lines += 1
        self.next_line_id += 1

    def delete_line(self, given_line):
        if self.selected_line == given_line:
            self.selected_line = None
        if self.hovered_line == given_line:
            self.hovered_line = None

        # Get the index and line from given_line
        id, line = given_line

        line.remove()  # Remove the line from the plot
        del self.lines[id]  # Remove the line from the dictionary
        self.number_lines -=1

        # Remove associated ranges
        for _range in list(self.ranges):  # Create a copy of the list to modify it during iteration
            if _range.contains(id):
                other_id = _range.other_index(id)
                if other_id in self.lines.keys():
                    _, other_line = self.lines[other_id][1]
                    other_line.remove()
                    del self.lines[other_id]
                    self.number_lines -=1
                self.ranges.remove(_range)
                self.needs_recalculate_ranges = True


        self.draw()

    def get_closest_line(self, posx, posy):
        closest = 1.0 * self.x_range
        closest_line = None
        if not posx or not posy:
            return closest_line

        for idx in self.lines.keys():
            _, (xdata, line) = self.lines[idx]
            dist = abs(xdata - posx)
            if dist < self.line_hover_precision * self.x_range:  # Threshold to select a line
                if dist < closest:
                    closest = dist
                    closest_line = (idx, line)
        return closest_line
    
    def sqr(self, x):
        return x * x
    def dist2(self, v, w):
        return self.sqr(v[0] - w[0]) + self.sqr(v[1] - w[1])
    def distToSegmentSquared(self, p, v, w):
        l2 = self.dist2(v, w)
        if (l2 == 0):
            return self.dist2(p, v)
        t = ((p[0] - v[0]) * (w[0] - v[0]) + (p[1] - v[1]) * (w[1] - v[1])) / l2
        t = max(0, min(1, t))
        return self.dist2(p, (v[0] + t * (w[0] - v[0]),
                        v[1] + t * (w[1] - v[1])))
    def distToSegment(self, p, v, w):
        return math.sqrt(self.distToSegmentSquared(p, v, w))

    def get_distance_to_curve(self, posx, posy):
        # Normalize distances
        ratio = self.x_range / self.y_range
        rx, ry = 1, 1/self.y_range

        # Find indexes nearest to posx
        indexes_nearest_x = self.nearest_datax_indexes(posx)
        dist_nearest = float('inf')
        closest_point = (None, None)

        for i in range(max(0, indexes_nearest_x[0] - 1), min(len(self.datax), indexes_nearest_x[1] + 2)):
            px, py = self.datax[i] * rx, (self.datay[i] + self.offset) * ry
            dist = np.hypot(px - posx * rx, py - posy * ry)
            if dist < dist_nearest:
                dist_nearest = dist
                closest_point = (px, py)

        #print("Closest point distance:", dist_nearest)
        #return closest_point
        return dist_nearest

    def nearest_datax_indexes(self, posx):
        # Binary search for the nearest index
        low, high = 0, len(self.datax) - 1
        best_idx = low
        while low <= high:
            mid = (low + high) // 2
            if self.datax[mid] < posx:
                low = mid + 1
            elif self.datax[mid] > posx:
                high = mid - 1
            else:
                best_idx = mid
                break
            # Update best_idx if the current mid is closer to the posx
            if abs(self.datax[mid] - posx) < abs(self.datax[best_idx] - posx):
                best_idx = mid

        # Return a range around the best index
        return max(0, best_idx - PLOT_MOUSE_INDEXES_DISTANCE_CHECKS), min(len(self.datax) - 1, best_idx + PLOT_MOUSE_INDEXES_DISTANCE_CHECKS)
    def nearest_datax_index(self, posx):
        #dycotomy time
        max = len(self.datax)
        a = 0
        b = max - 1
        center = int((a + b) / 2)
        lst_center = -1

        if self.datax[a] > posx:
            return a
        if self.datax[b] < posx:
            return b

        it = 0
        while center != lst_center:
            if self.datax[center] > posx:
                b = center
            else:
                a = center
            lst_center = center
            center = int((a + b) / 2)
            it = it + 1

        return center
    def nearest_cluster_index(self, posx):
        #dycotomy time
        max = len(self.spikes_clusters)
        if not max:
            print("empty list of clusters...")
            return 0
        a = 0
        b = max - 1
        center = int((a + b) / 2)
        lst_center = -1
        if self.spikes_clusters[a].spikesX[0] > posx:
            return a
            
        if self.spikes_clusters[b].spikesX[0] < posx:
            return b

        it = 0
        while center != lst_center:
            if self.spikes_clusters[center].spikesX[0] > posx:
                b = center
            else:
                a = center
            lst_center = center
            center = int((a + b) / 2)
            it = it + 1
            
        return center
    
    def update_line_data(self, line_to_update, posx, posy):
        id, line = line_to_update
        #line.set_color(color)
        if posx and posy:
            line.set_xdata([posx] * 2)
            self.lines[id] = (id, (posx, line))  # Update the line's position in the dictionary
            self.needs_recalculate_ranges = True
        self.draw()

    def update_ranges(self):
        ri = 0
        total_gx = []
        total_gy = []

        for r in self.ranges:
            start = self.lines[r.start_index][1][0]
            end = self.lines[r.end_index][1][0]
            #if start and end:
            r.start_pos = start
            r.end_pos = end
            r.auto_correct()

        first_range = True
        for r in self.ranges:
            for r2 in self.ranges[ri+1:]:
                if r != r2:
                    r.resolve(r2)
            ri = ri + 1

            if not first_range:
                # Add NaN values to "break" the line between ranges
                total_gx.append(np.nan)
                total_gy.append(np.nan)
            first_range = False

            x = []
            y = []

            if self.range_mode == RANGE_MODE_FULL:
                startCl = self.nearest_datax_index(r.start_pos)
                endCl = self.nearest_datax_index(r.end_pos) + 1
                x = self.datax[startCl:endCl]
                y = self.datay[startCl:endCl]
            if self.range_mode == RANGE_MODE_CLUSTERS:
                startCl = self.nearest_cluster_index(r.start_pos)
                endCl = self.nearest_cluster_index(r.end_pos) + 1
                x, y = loader.graph_DPT(self.spikes_clusters[startCl:endCl])
            total_gx.extend(x)
            total_gy.extend(y)
        
        self.set_selection_data(total_gx, total_gy)

    def apply_color_palette(self):
        for idx in self.lines.keys():
            _, (xdata, line) = self.lines[idx]
            if not self.enabled:
                line.set_color(self.color_palette.get_color(PALETTE_OBJECT_LINE, PALETTE_PROPERTY_LINE_DISABLED))
                continue
            if self.selected_line and self.selected_line[1] == line:
                line.set_color(self.color_palette.get_color(PALETTE_OBJECT_LINE, PALETTE_PROPERTY_LINE_SELECTED))
            elif self.hovered_line and self.hovered_line[1] == line:
                line.set_color(self.color_palette.get_color(PALETTE_OBJECT_LINE, PALETTE_PROPERTY_LINE_HOVERED))
            else:
                line.set_color(self.color_palette.get_color(PALETTE_OBJECT_LINE, PALETTE_PROPERTY_LINE_ENABLED))

        if self.hovered:
            self.graph.set_color(self.color_palette.get_color(PALETTE_OBJECT_GRAPH, PALETTE_PROPERTY_PLOT_HOVERED))
            self.graph_selections.set_color(self.color_palette.get_color(PALETTE_OBJECT_GRAPH, PALETTE_PROPERTY_PLOT_HOVERED))
        else:
            if self.enabled:
                self.graph.set_color(self.color_palette.get_color(PALETTE_OBJECT_GRAPH, PALETTE_PROPERTY_PLOT_ENABLED))
                self.graph_selections.set_color(self.color_palette.get_color(PALETTE_OBJECT_GRAPH_SELECTION, PALETTE_PROPERTY_PLOT_ENABLED))
            else:
                self.graph.set_color(self.color_palette.get_color(PALETTE_OBJECT_GRAPH, PALETTE_PROPERTY_PLOT_DISABLED))
                self.graph_selections.set_color(self.color_palette.get_color(PALETTE_OBJECT_GRAPH_SELECTION, PALETTE_PROPERTY_PLOT_DISABLED))

    def draw(self):
        if self.lod.update():
            dx, dy = self.lod.get_compressed_data(self.datax, self.datay)
            self.set_data(dx, dy)

        if self.needs_recalculate_ranges:
            self.update_ranges()
            self.needs_recalculate_ranges = False

        self.apply_color_palette()



class SelectionRange:
    def __init__(self, start_index, start_pos, end_index, end_pos):
        self.start_index = start_index
        self.end_index = end_index
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.auto_correct()

    def contains(self, index):
        return self.start_index == index or self.end_index == index
    def other_index(self, index):
        if self.contains(index):
            if index == self.start_index:
                return self.end_index
            else:
                return self.start_index
        return -1

    def auto_correct(self):
        if not self.start_pos or not self.end_pos:
            return -1
        if self.start_pos > self.end_pos:
            dt_index = self.start_index
            self.start_index = self.end_index
            self.end_index = dt_index
            dt_pos = self.start_pos
            self.start_pos = self.end_pos
            self.end_pos = dt_pos
        return 0

    def resolve(self, other_range):
        r = self.auto_correct()
        r2 = other_range.auto_correct()
        if r == -1 or r2 == -1:
            return
        if self.start_pos < other_range.start_pos and other_range.end_pos < self.end_pos:
            dt_index = self.end_index
            self.end_index = other_range.end_index
            other_range.end_index = dt_index
            dt_pos = self.end_pos
            self.end_pos = other_range.end_pos
            other_range.end_pos = dt_pos

            dt_index = self.end_index
            self.end_index = other_range.start_index
            other_range.start_index = dt_index
            dt_pos = self.end_pos
            self.end_pos = other_range.start_pos
            other_range.start_pos = dt_pos
            return
        if self.start_pos < other_range.start_pos and other_range.start_pos < self.end_pos:
            dt_index = other_range.start_index
            other_range.start_index = self.end_index
            self.end_index = dt_index
            dt_pos = other_range.start_pos
            other_range.start_pos = self.end_pos
            self.end_pos = dt_pos
            return
        if self.start_pos < other_range.end_pos and other_range.end_pos < self.end_pos:
            dt_index = self.start_index
            self.start_index = other_range.end_index
            other_range.end_index = dt_index
            dt_pos = self.start_pos
            self.start_pos = other_range.end_pos
            other_range.end_pos = dt_pos
            return