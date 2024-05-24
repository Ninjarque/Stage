import math
import numpy as np

class FeatureFilter:
    def __init__(self, values):
        self.values = values

    # actually, we'll see about centering depending on the format of the curve -> no format, no centering
    # but we need to resize it to be "normalized" in terms of width, we'll see about that though
    def format(self, curvex, curvey, indexes_count):
        # Normalize curvey
        m = max(curvey)
        if m == 0.0:
            print("Empty or null curve unformattable...")
            return [0] * indexes_count
        avg = np.mean(curvey)
        ignore_norm_ratio = 0.3
        normalized_y = [y / m * ((1 - ignore_norm_ratio) + m * ignore_norm_ratio) for y in curvey]

        # Interpolation
        if indexes_count != len(curvex):
            #print("Indexes count", indexes_count, "vs curvex length", len(curvex), ", normalized y being of size", len(normalized_y))
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
        ncurvex = np.array(curvex)
        ncurvey = np.array(curvey)
        formatted_curve = self.format(ncurvex, ncurvey, len(self.values))
        #print("FORMATTED CURVE len", len(formatted_curve), "max", max(formatted_curve), "min", min(formatted_curve), "it is")
        #print("FILTER len", len(self.values), "max", max(self.values), "min", min(self.values), "it is")
        return self.mult_extract(formatted_curve, self.values)