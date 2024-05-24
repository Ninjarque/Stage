import numpy as np
from noise import pnoise1
import random

from FeatureFilter import *

FEATURE_EXTRACTOR_SLIDING_STEP = 2
FEATURE_EXTRACTOR_TRUNCATE_RATIO = 0.1 #0.0

def generate_noise_curve(length, scale=1.0, octaves=1, persistence=0.5, lacunarity=2.0, seed=None):
    if seed is not None:
        random.seed(seed)
    # Use random offsets to introduce variability
    offset = random.uniform(0, 100000000)
    return [pnoise1((i + offset) / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity) for i in range(length)]

class RandomFeatureExtractor:
    def __init__(self, filters_x_length, features_count = 20, seed=None):
        self.features_count = features_count
        self.filters_x_length = filters_x_length
        self.feature_filters = []
        self.filters = []
        for i in range(self.features_count):
            values = generate_noise_curve(self.filters_x_length, scale=100.0, seed=seed)
            self.filters.append(FeatureFilter(values))

    def extract_features(self, curvex, curvey):
        features = []
        for filter in self.filters:
            f = filter.apply(curvex, curvey)
            features.append(f)

        return features
    
    def distance(self, target_features, current_features):
        dt = np.array(target_features) - np.array(current_features)
        d = np.linalg.norm(dt)
        return d

    def sliding_distance(self, target_curvex, target_curvey, current_curvex, current_curvey, sliding_step, truncate_smaller_curve_ratio = 0.0):
        # Determine which curve is smaller
        if len(current_curvex) < len(target_curvex):
            smaller_curvex, smaller_curvey = current_curvex, current_curvey
            larger_curvex, larger_curvey = target_curvex, target_curvey
        else:
            smaller_curvex, smaller_curvey = target_curvex, target_curvey
            larger_curvex, larger_curvey = current_curvex, current_curvey

        min_dist = -1
        min_index = -1
        window_size = len(smaller_curvex)

        target_features = self.extract_features(smaller_curvex, smaller_curvey)

        # Slide the smaller curve along the larger curve
        for start in range(0, len(larger_curvex) - window_size + 1, sliding_step):
            sub_curvex = larger_curvex[start:start + window_size]
            sub_curvey = larger_curvey[start:start + window_size]
            current_features = self.extract_features(sub_curvex, sub_curvey)
            dist = self.distance(target_features, current_features)
            if min_dist == -1 or dist < min_dist:
                min_dist = dist
                min_index = start

        return min_dist, min_index
    
    def truncate_curve(self, curvex, curvey, ratio):
        startI = 0
        curr_y = curvey[startI]
        smaller_truncate_threshold = max(curvey) * ratio
        while startI < len(curvey) and curr_y < smaller_truncate_threshold:
            curr_y = curvey[startI]
            startI += 1
        endI = len(curvey) - 1
        curr_y = curvey[endI]
        while endI >= 0 and curr_y < smaller_truncate_threshold:
            curr_y = curvey[endI]
            endI -= 1

        #if startI != 0 or endI != len(curvey):
        #    print("actually doing something? [", startI, ",", endI, "], originaly [", 0, ",", len(curvey), "]")

        curvex = curvex[startI:endI]
        curvey = curvey[startI:endI]

        return curvex, curvey

    def match(self, target_curvex, target_curvey, list_curvex, list_curvey):
        sliding_step = FEATURE_EXTRACTOR_SLIDING_STEP
        truncate_smaller = FEATURE_EXTRACTOR_TRUNCATE_RATIO
        best_index = -1
        best_dist = -1

        target_curvex, target_curvey = self.truncate_curve(target_curvex, target_curvey, truncate_smaller)


        for i in range(len(list_curvex)):
            cx = list_curvex[i]
            cy = list_curvey[i]
            cx, cy = self.truncate_curve(cx, cy, truncate_smaller)
            dist, index = self.sliding_distance(target_curvex, target_curvey, cx, cy, sliding_step)
            print("dist", dist, "at", index, "for chunk [", cx[0], ",", cx[-1], "]")
            if best_index == -1 or dist < best_dist:
                best_index = i
                best_dist = dist

        return best_index
