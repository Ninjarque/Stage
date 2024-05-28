import math
import numpy as np


class FeatureFilter:
    def __init__(self, values):
        self.values = values
        self.indexes = [i for i in range(len(self.values))]


    def mult_extract(self, curve, values):
        c = np.array(curve)
        f = np.array(values)
        
        return np.sum(np.multiply(c, f))
        #return np.abs(np.sum(np.multiply(c, f)))

    def apply(self, curvex, curvey):
        #ncurvex = np.array(curvex)
        #ncurvey = np.array(curvey)
        #formatted_curve = self.format(ncurvex, ncurvey, len(self.values))
        curvex_coords = [i for i in range(len(curvex))]
        formatted_values = np.interp(curvex_coords, self.indexes, self.values)
        #print("formatted filter values", formatted_values)

        #print("FORMATTED CURVE len", len(formatted_curve), "max", max(formatted_curve), "min", min(formatted_curve), "it is")
        #print("FILTER len", len(self.values), "max", max(self.values), "min", min(self.values), "it is")
        return self.mult_extract(curvey, formatted_values)#self.mult_extract(formatted_curve, self.values)