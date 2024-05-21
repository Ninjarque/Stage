from math import *

import dichotomy

LOD_RECOMPUTE_RATIO_THRESHOLD = 0.1

class LODCurveManager:
    def __init__(self, ax, data_len, max_displayed_data):
        self.ax = ax
        self.fig = ax.figure
        self.max_displayed_data = max_displayed_data
        self.init_data_len = data_len
        
        self.x_min = -1
        self.x_max = -1

        self.update()

    def update(self):
        # Get current x-axis limits
        x_min, x_max = self.ax.get_xlim()
        changed = False
        if x_min != self.x_min or x_max != self.x_max:
            changed = True
        self.x_min = x_min
        self.x_max = x_max

        return changed

    def get_compressed_data(self, datax, datay):
        imin = dichotomy.nearest_index(self.x_min, datax)
        imax = dichotomy.nearest_index(self.x_max, datax)

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

        self.update()

    def update(self):
        # Get current x-axis limits
        x_min, x_max = self.ax.get_xlim()
        changed = False
        if x_min != self.x_min or x_max != self.x_max:
            changed = True
        self.x_min = x_min
        self.x_max = x_max

        return changed

    def get_compressed_data(self, xdata, *data_lists):
        imin = dichotomy.nearest_index(self.x_min, xdata)
        imax = dichotomy.nearest_index(self.x_max, xdata) + 1
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