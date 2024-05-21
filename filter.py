import math

FILTER_VALIDATION_THRESHOLD = 0.5

class Filter:
    def __init__(self, x_start, x_end, function, validation_threshold = FILTER_VALIDATION_THRESHOLD):
        self.x_start = x_start
        self.x_end = x_end
        self.function = function
        self.validation_threshold = validation_threshold

    def select(self, curve, x_start, x_end):
        pass

    def normalize(self, curve):
        pass


    def apply(self, curve):
        if not curve:
            return False
        
        curve = self.select(curve, self.x_start, self.x_end)
        if not curve:
            return False
        curve = self.normalize(curve)
        flt = self.function(curve)

        return flt > self.validation_threshold