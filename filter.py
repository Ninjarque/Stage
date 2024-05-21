import math
import dichotomy

FILTER_VALIDATION_THRESHOLD = 0.5

class Filter:
    def __init__(self, x_start, x_end, function, validation_threshold = FILTER_VALIDATION_THRESHOLD):
        self.x_start = x_start
        self.x_end = x_end
        self.function = function
        self.validation_threshold = validation_threshold

    def select(self, curve, x_start, x_end):
        c_start = dichotomy.nearest_index(x_start, curve)
        c_end = dichotomy.nearest_index(x_end, curve)
        if c_start < 0 or c_end >= len(curve):
            return []
        return curve[c_start:c_end]

    # actually, we'll see about centering depending on the format of the curve -> no format, no centering
    # but we need to resize it to be "normalized" in terms of width, we'll see about that though
    def format(self, curve):
        m = max(curve)
        normalized = [x / m for x in curve]

        return normalized


    def apply(self, curve):
        if not curve:
            return False
        
        curve = self.select(curve, self.x_start, self.x_end)
        if not curve:
            return False
        curve = self.format(curve)
        flt = self.function(curve)

        return flt > self.validation_threshold