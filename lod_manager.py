from math import *

import dichotomy

LOD_CURVE_RECOMPUTE_RATIO_THRESHOLD = 0.3
LOD_BAR_RECOMPUTE_RATIO_THRESHOLD = 0.3


class LODCurveManager:
    def __init__(self, ax, data_len, max_displayed_data):
        self.ax = ax
        self.fig = ax.figure
        self.max_displayed_data = max_displayed_data
        self.init_data_len = data_len
        
        self.x_min = -1
        self.x_max = -1
        self.x_margins = 0

        self.update()

    def dist_ratio(self, new_x_min, new_x_max):
        rx = new_x_max - new_x_min
        dx = abs(self.x_min - new_x_min) + abs(self.x_max - new_x_max)
        return dx / rx

    def update(self):
        # Get current x-axis limits
        x_min, x_max = self.ax.get_xlim()
        changed = False
        dr = self.dist_ratio(x_min, x_max)
        #if x_min != self.x_min or x_max != self.x_max:
        if dr > LOD_CURVE_RECOMPUTE_RATIO_THRESHOLD:
            changed = True
            self.x_min = x_min
            self.x_max = x_max
            self.x_margins = (x_max - x_min) / 2 * LOD_CURVE_RECOMPUTE_RATIO_THRESHOLD
            #print("Recomputing LOD, ratio of:", dr)

        return changed

    def get_compressed_data(self, datax, datay):
        imin = dichotomy.nearest_index(self.x_min - self.x_margins / 2, datax)
        imax = dichotomy.nearest_index(self.x_max + self.x_margins / 2, datax)

        datax = datax[imin:imax]
        datay = datay[imin:imax]

        if len(datax) > self.max_displayed_data:
            l = int(len(datax) / self.max_displayed_data)
            datax = datax[::l]
            datay = datay[::l]
        
        return datax, datay

class LODBarManager:
    def __init__(self, ax, data_len, max_displayed_data):
        self.ax = ax
        self.fig = ax.figure
        self.max_displayed_data = max_displayed_data
        self.init_data_len = data_len
        
        self.x_min = -1
        self.x_max = -1
        self.x_margins = 0

        self.update()

    def dist_ratio(self, new_x_min, new_x_max):
        rx = new_x_max - new_x_min
        dx = abs(self.x_min - new_x_min) + abs(self.x_max - new_x_max)
        return dx / rx

    def update(self):
        # Get current x-axis limits
        x_min, x_max = self.ax.get_xlim()
        changed = False
        dr = self.dist_ratio(x_min, x_max)
        #if x_min != self.x_min or x_max != self.x_max:
        if dr > LOD_BAR_RECOMPUTE_RATIO_THRESHOLD:
            changed = True
            self.x_min = x_min
            self.x_max = x_max
            self.x_margins = (x_max - x_min) / 2 * LOD_BAR_RECOMPUTE_RATIO_THRESHOLD
            #print("Recomputing bar LOD, ratio of:", dr)

        return changed

    def get_compressed_data(self, xdata, *data_lists):
        imin = dichotomy.nearest_index(self.x_min - self.x_margins, xdata)
        imax = dichotomy.nearest_index(self.x_max + self.x_margins, xdata) + 1
        imax = min(imax, len(xdata) - 1)
        
        xdata = xdata[imin:imax]
        compressed_data_lists = [xdata]
        
        for data in data_lists:
            data = data[imin:imax]
            if len(data) > self.max_displayed_data:
                l = int(len(data) / self.max_displayed_data)
                data = data[::l]
            compressed_data_lists.append(data)
        
        if len(xdata) > self.max_displayed_data:
            l = int(len(xdata) / self.max_displayed_data)
            xdata = xdata[::l]
            compressed_data_lists[0] = xdata
        
        return tuple(compressed_data_lists)