import numpy as np
#from noise import pnoise1
import random
import matplotlib.pyplot as plt

from abc import ABC, abstractmethod

import dichotomy

from FeatureFilter import *

FEATURE_EXTRACTOR_SLIDING_STEP = 1
FEATURE_EXTRACTOR_TRUNCATE_RATIO = 0.01 #0.0

DEBUG_FEATURE = False

'''
def generate_noise_curve(length, scale=1.0, octaves=4, persistence=0.5, lacunarity=2.0, seed=None):
    if seed is not None:
        random.seed(seed)
    return [pnoise1(i / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity) for i in range(length)]

def generate_noise_curve(length, scale=1.0, frequency=1.0, octaves=4, persistence=0.5, lacunarity=2.0, seed=None):
    if seed is not None:
        random.seed(seed)
    
    def interpolate(a0, a1, w):
        return (a1 - a0) * w + a0
    
    def perlin(x):
        x0 = int(x)
        x1 = x0 + 1
        sx = x - x0
        
        n0 = random.uniform(-1, 1)
        n1 = random.uniform(-1, 1)
        
        ix0 = interpolate(n0, n1, sx)
        return ix0
    
    noise_values = np.zeros(length)
    #frequency = 1.0
    amplitude = 1.0
    max_amplitude = 0.0
    
    for _ in range(octaves):
        for i in range(length):
            noise_values[i] += perlin(i / scale * frequency) * amplitude
        frequency *= lacunarity
        amplitude *= persistence
        max_amplitude += amplitude
    
    return noise_values / max_amplitude
'''

def fade(t):
    return t * t * t * (t * (t * 6 - 15) + 10)

def lerp(t, a, b):
    return a + t * (b - a)

def grad(hash, x):
    h = hash & 15
    grad = 1 + (h & 7)  # Gradient value is one of 1, 2, ..., 8
    if h & 8:
        grad = -grad
    return grad * x

def perlin(x, perm):
    X = int(np.floor(x)) & 255
    x -= np.floor(x)
    u = fade(x)
    
    a = perm[X]
    b = perm[X + 1]
    
    return lerp(u, grad(a, x), grad(b, x - 1))

def generate_perlin_noise_1d(size, scale=100, seed=0, octaves=8, persistence=0.5):
    np.random.seed(seed)
    perm = np.arange(256, dtype=int)
    np.random.shuffle(perm)
    perm = np.stack([perm, perm]).flatten()

    noise = np.zeros(size)
    max_amplitude = 0
    amplitude = 1
    frequency = 1
    for _ in range(octaves):
        offset = np.random.uniform(0, 1000000)
        for i in range(size):
            x = (i + offset) / scale * frequency
            noise[i] += perlin(x, perm) * amplitude
        max_amplitude += amplitude
        amplitude *= persistence
        frequency *= 2

    return noise / max_amplitude

class FeatureExtractor(ABC):
    @abstractmethod
    def extract_features(self, curvex, curvey):
        pass
    
    @abstractmethod
    def distance(self, target_curvex, target_curvey, current_curvex, current_curvey, target_features, current_features):
        pass

    def sliding_distance(self, target_curvex, target_curvey, current_curvex, current_curvey, sliding_step):
        # Determine which curve is smaller
        if len(current_curvex) < len(target_curvex):
            smaller_curvex, smaller_curvey = current_curvex, current_curvey
            larger_curvex, larger_curvey = target_curvex, target_curvey
        else:
            smaller_curvex, smaller_curvey = target_curvex, target_curvey
            larger_curvex, larger_curvey = current_curvex, current_curvey

        min_dist = -1
        min_index_start = -1
        min_index_end = -1
        #window_size = len(smaller_curvex)

        target_features = self.extract_features(smaller_curvex, smaller_curvey)

        target_start_offset_x = smaller_curvex[0]
        target_end_offset_x = smaller_curvex[-1]
        target_offset_x = target_end_offset_x - target_start_offset_x
        current_start_offset_x = larger_curvex[0]
        current_end_offset_x_index = dichotomy.nearest_index(current_start_offset_x + target_offset_x, larger_curvex)
        window_size = current_end_offset_x_index

        # Slide the smaller curve along the larger curve
        for start in range(0, len(larger_curvex) - window_size + 1, sliding_step):
            sub_curvex = larger_curvex[start:start + window_size]
            sub_curvey = larger_curvey[start:start + window_size]
            current_features = self.extract_features(sub_curvex, sub_curvey)
            dist = self.distance(smaller_curvex, smaller_curvey, sub_curvex, sub_curvey, target_features, current_features)
            #print("Window, ", start, ":", start + window_size, " considering max size:", len(larger_curvex))
            #print("dist", dist, "for window", start, ":", start + window_size)
            if min_dist == -1 or dist < min_dist:
                #print("Found better dist, from", min_dist, "to", dist, ", at pos [", start, ":", start + window_size, "]")
                min_dist = dist
                min_index_start = start
                min_index_end = start + window_size

                if DEBUG_FEATURE:
                    sucx = np.array(sub_curvex) - sub_curvex[0]
                    smcx = np.array(smaller_curvex) - smaller_curvex[0]
                    plt.suptitle('Distance feature, dist:{}'.format(min_dist))
                    plt.plot(sucx, sub_curvey, 'b-')
                    plt.plot(smcx, smaller_curvey, 'r-')
                    plt.show()
                

        if len(current_curvex) < len(target_curvex):
            min_index_start = 0
            min_index_end = -1

        return min_dist, min_index_start, min_index_end
    
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

        print("truncated from [", 0, ",", len(curvey) - 1, "] to [", startI, ",", endI, "], with threshold of ", smaller_truncate_threshold, "/", max(curvey))

        curvex = curvex[startI:endI]
        curvey = curvey[startI:endI]

        return curvex, curvey, startI, endI

    def match(self, target_curvex, target_curvey, current_curvex, current_curvey, sliding_step_precision = 1.0):
        if sliding_step_precision <= 0.01:
            sliding_step_precision = 0.01
        sliding_step = int(max(FEATURE_EXTRACTOR_SLIDING_STEP / sliding_step_precision, 1))
        truncate_smaller = FEATURE_EXTRACTOR_TRUNCATE_RATIO

        target_maxy = max(target_curvey)
        target_curvey = [y / target_maxy for y in target_curvey]

        target_curvex, target_curvey, target_start, target_end = self.truncate_curve(target_curvex, target_curvey, truncate_smaller)

        current_maxy = max(current_curvey)
        current_curvey = [y / current_maxy for y in current_curvey]

        cx, cy, coffset, cend = self.truncate_curve(current_curvex, current_curvey, truncate_smaller)
        dist, start, end = self.sliding_distance(target_curvex, target_curvey, cx, cy, sliding_step)
        print("dist", dist, "from", start, "to", end, " [", cx[0], ",", cx[-1], "]")
        
        return target_start, target_end, start, end, dist


class RandomFeatureExtractor(FeatureExtractor):
    def __init__(self, filters_x_length, features_count = 20, seed=None):
        random.seed(seed)
        self.features_count = features_count
        self.filters_x_length = filters_x_length
        self.feature_filters = []
        self.filters = []
        for i in range(self.features_count):
            values = generate_perlin_noise_1d(self.filters_x_length, scale=filters_x_length/4.0, seed=seed)
            #if i == 0:
            #    print(values)
            
            #plt.suptitle('Filter {}'.format(i))
            #plt.plot([i for i in range(self.filters_x_length)], values, 'b-')
            #plt.show()
            
            self.filters.append(FeatureFilter(values))

    def extract_features(self, curvex, curvey):
        features = []
        for filter in self.filters:
            f = filter.apply(curvex, curvey)
            features.append(f)

        features = features / np.linalg.norm(features)

        return features
    
    def distance(self, target_curvex, target_curvey, current_curvex, current_curvey, target_features, current_features):
        #target_curvex = np.array(target_curvex) - target_curvex[0]
        #current_curvex = np.array(current_curvex) - current_curvex[0]
        
        _dt = np.array(target_features) - np.array(current_features)
        df = np.sum(np.abs(_dt))#np.linalg.norm(dt)

        dx = np.abs(target_curvex[0] - current_curvex[0])

        rf = 0.1
        rx = 16.0
        d = (df * rf + dx * rx) / (rf + rx)

        #print("dist feature:", d_features, "dist curve's y:", d_curvey, "total dist:", d)

        return d

class ShapeFeatureExtractor(FeatureExtractor):
    def __init__(self, scales = [0.75, 1.0, 1.25, 1.5]):
        self.scales = scales

    def extract_features(self, curvex, curvey):
        return []
    
    def distance(self, target_curvex, target_curvey, current_curvex, current_curvey, target_features, current_features):
        min_dist = -1
        for scale in self.scales:
            current_x = [i - len(current_curvex) / 2 for i in range(len(current_curvex))]
            target_x = [(i - len(target_curvey) / 2) * scale for i in range(len(target_curvey))]

            new_target_curvey = np.interp(current_x, target_x, target_curvey)
            dt = np.array(new_target_curvey) - np.array(current_curvey)
            d_curvey = np.sum(np.abs(dt))
            

            if min_dist == -1 or d_curvey < min_dist:
                min_dist = d_curvey

        return min_dist
    
class DistanceFeatureExtractor(FeatureExtractor):
    def __init__(self, scales = [0.75, 1.0, 1.25, 1.5], shape_ratio = 1.0, x_dist_ratio = 10.0):
        self.scales = scales
        self.shape_ratio = shape_ratio
        self.x_dist_ratio = x_dist_ratio

    def extract_features(self, curvex, curvey):
        return []
    
    def distance(self, target_curvex, target_curvey, current_curvex, current_curvey, target_features, current_features):
        min_dist = -1
        for scale in self.scales:
            current_x = [i - len(current_curvex) / 2 for i in range(len(current_curvex))]
            target_x = [(i - len(target_curvey) / 2) * scale for i in range(len(target_curvey))]
            
            new_target_curvey = np.interp(current_x, target_x, target_curvey)
            dt = np.array(new_target_curvey) - np.array(current_curvey)
            d_curvey = np.sum(np.abs(dt))


            dx = np.abs(target_curvex[0] - current_curvex[0])

            d = (d_curvey * self.shape_ratio + dx * self.x_dist_ratio) / (self.shape_ratio + self.x_dist_ratio)
            

            if min_dist == -1 or d < min_dist:
                min_dist = d

        return min_dist