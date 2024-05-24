import math
import numpy as np

class FeatureFilter:
    def __init__(self, values):
        self.values = values

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

    def mult_extract(self, curve, values):
        c = np.array(curve)
        f = np.array(values)
        
        return np.sum(np.multiply(c, f))


    def apply(self, curvex, curvey):
        if not curvex or not curvey:
            return 0
        ncurvex = np.array(curvex)
        ncurvey = np.array(curvey)
        formatted_curve = self.format(ncurvex, ncurvey, len(self.values))
        return self.mult_extract(formatted_curve, self.values)