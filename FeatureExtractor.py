import numpy as np
from noise import pnoise1

from FeatureFilter import *

def generate_noise_curve(length, scale=1.0, octaves=1, persistence=0.5, lacunarity=2.0):
    return [pnoise1(i / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity) for i in range(length)]


class RandomFeatureExtractor:
    def __init__(self, filters_x_length, features_count = 20):
        self.features_count = features_count
        self.filters_x_length = filters_x_length
        self.feature_filters = []
        self.filters = []
        for i in range(self.features_count):
            values = generate_noise_curve(self.filters_x_length)
            self.filters.append(FeatureFilter(values))

    def extract_features(self, curvex, curvey):
        features = []
        for filter in self.filters:
            f = filter.apply(curvex, curvey)
            features.append(f)

        return features
    
    def distance(self, target_curvex, target_curvey, current_curvex, current_curvey):
        target_features = self.extract_features(target_curvex, target_curvey)
        current_features = self.extract_features(current_curvex, current_curvey)

        return np.linalg.norm(np.array(target_features) - np.array(current_features))

    def match(self, target_curvex, target_curvey, list_curvex, list_curvey):
        best_index = -1
        best_dist = -1

        for i in range(list_curvex):
            cx = list_curvex[i]
            cy = list_curvey[i]
            dist = self.distance(target_curvex, target_curvey, cx, cy)
            if best_index == -1 or dist < best_dist:
                best_index = i
                best_dist = dist

        return best_index
