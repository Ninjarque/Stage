from math import *

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
        imin = self.nearest_datax_index(self.x_min, datax)
        imax = self.nearest_datax_index(self.x_max, datax)

        datax = datax[imin:imax]
        datay = datay[imin:imax]

        if len(datax) > self.max_displayed_data:
            l = int(len(datax) / self.max_displayed_data)
            datax = datax[::l]
            datay = datay[::l]
        
        return datax, datay
    
    def nearest_datax_index(self, posx, data):
        #dycotomy time
        max = len(data)
        a = 0
        b = max - 1
        center = int((a + b) / 2)
        lst_center = -1

        if data[a] > posx:
            return a
        if data[b] < posx:
            return b

        it = 0
        while center != lst_center:
            if data[center] > posx:
                b = center
            else:
                a = center
            lst_center = center
            center = int((a + b) / 2)
            it = it + 1

        return center

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

    def get_compressed_data(self, data):
        imin = self.nearest_datax_index(self.x_min, data)
        imax = self.nearest_datax_index(self.x_max, data)
        data = data[imin:imax]

        if len(data) > self.max_displayed_data:
            l = int(len(data) / self.max_displayed_data)
            data = data[::l]
        
        return data
    
    def nearest_datax_index(self, posx, data):
        #dycotomy time
        max = len(data)
        a = 0
        b = max - 1
        center = int((a + b) / 2)
        lst_center = -1

        if data[a] > posx:
            return a
        if data[b] < posx:
            return b

        it = 0
        while center != lst_center:
            if data[center] > posx:
                b = center
            else:
                a = center
            lst_center = center
            center = int((a + b) / 2)
            it = it + 1

        return center