import math
import dichotomy
import numpy as np

FILTER_DIST_VALIDATION_THRESHOLD = 0.5
FILTER_FUNCTION_SPAN = 1000

class Filter:
    def __init__(self, x_start, x_end, function_values, validation_threshold = FILTER_DIST_VALIDATION_THRESHOLD):
        self.x_start = x_start
        self.x_end = x_end
        self.function_values = function_values
        self.validation_threshold = validation_threshold

    def select(self, curvex, curvey, x_start, x_end):
        c_start = dichotomy.nearest_index(x_start, curvex)
        c_end = dichotomy.nearest_index(x_end, curvex)
        if c_start < 0 or c_end >= len(curvex):
            return [], []
        return curvex[c_start:c_end], curvey[c_start:c_end]

    # actually, we'll see about centering depending on the format of the curve -> no format, no centering
    # but we need to resize it to be "normalized" in terms of width, we'll see about that though
    def format(self, curvex, curvey, indexes_count):
        if not curvex or not curvey:
            return []

        # Normalize curvey
        m = max(curvey)
        normalized_y = [y / m for y in curvey]

        # Interpolation
        if indexes_count != len(curvex):
            x_interpolated = np.linspace(curvex[0], curvex[-1], indexes_count)
            y_interpolated = np.interp(x_interpolated, curvex, normalized_y)
        else:
            x_interpolated = curvex
            y_interpolated = normalized_y

        return y_interpolated

    def dist(self, curve, function_values):
        c = np.array(curve)
        f = np.array(function_values)
        
        return np.sum(np.absolute(c - f))


    def apply(self, curvex, curvey):
        if not curvex or not curvey:
            return False
        
        curvex, curvey = self.select(curvex, curvey, self.x_start, self.x_end)
        if not curvex or not curvey:
            return False, None, None
        
        ncurvex = np.array(curvex)
        ncurvey = np.array(curvey)
        formatted_curve = self.format(ncurvex, ncurvey, len(self.function_values))
        flt = self.dist(formatted_curve, self.function_values)

        # considered as integral somehow
        distToOrigin = np.sum(np.absolute(formatted_curve))

        #dist to curve, compared to a percentage of integral, should be the ratio to which it matchs the curve... hopefully
        return flt < distToOrigin * self.validation_threshold, curvex, curvey