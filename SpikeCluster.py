import numpy as np

import dichotomy

SPIKE_CLUSTER_NOISE_Y_THRESHOLD = 0.035

class SpikeCluster:
    startI = 0
    countI = 0

    spikesX = []
    spikesY = []
    
    bars = []

    def __init__(self, startI, countI, spikesX, spikesY, bars = []):
        self.startI = startI
        self.countI = countI
        self.spikesX = spikesX
        self.spikesY = spikesY
        self.bars = bars

    def __lt__(self, other):
        if not self.spikesX:
            if not other.spikesX:
                return False
            return True
        if not other.spikesX:
            return False
        return self.spikesX[-1] < other.spikesX[0]

    def is_over_noise_threshold(self, threshold_ratio=1.0, mean_or_max_ratio = 0.5):
        max_ratio = 1.0 - mean_or_max_ratio
        mean_ratio = mean_or_max_ratio
        m = (np.max(self.spikesY) * max_ratio + np.mean(self.spikesY) * mean_ratio) / (max_ratio + mean_ratio)
        return m > threshold_ratio * SPIKE_CLUSTER_NOISE_Y_THRESHOLD
    
    def merge(clusters):
        startI = 0
        countI = 0

        spikesX = []
        spikesY = []
        
        bars = []
        for c in clusters:
            if startI == -1 or startI > c.startI:
                startI = c.startI
            countI += c.countI
            spikesX = spikesX + c.spikesX
            spikesY = spikesY + c.spikesY
            bars = bars + c.bars
        return SpikeCluster(startI, countI, spikesX, spikesY, bars)
    
    def compile(clusters, bars):
        spikes = SpikeCluster.merge(clusters)
        spikes.bars = bars
        return spikes
    
    def truncate(cluster, ratio, regrow = 0):
        startI = 0
        curr_y = cluster.spikesY[startI]
        smaller_truncate_threshold = max(cluster.spikesY) * ratio
        while startI < len(cluster.spikesY) and curr_y < smaller_truncate_threshold:
            curr_y = cluster.spikesY[startI]
            startI += 1
        endI = len(cluster.spikesY) - 1
        curr_y = cluster.spikesY[endI]
        while endI >= 0 and curr_y < smaller_truncate_threshold:
            curr_y = cluster.spikesY[endI]
            endI -= 1

        #if startI != 0 or endI != len(self.spikesY):
        #    print("actually doing something? [", startI, ",", endI, "], originaly [", 0, ",", len(self.spikesY), "]")

        truncated_length = endI - startI + 1
        regrow_length = int(truncated_length * regrow / 2.0)

        startI = max(0, startI - regrow_length)
        endI = min(len(cluster.spikesY) - 1, endI + regrow_length)

        print("truncated from [", 0, ",", len(cluster.spikesY) - 1, "] to [", startI, ",", endI, "], with threshold of ", smaller_truncate_threshold, "/", max(cluster.spikesY))

        spikesX = cluster.spikesX[startI:endI+1]
        spikesY = cluster.spikesY[startI:endI+1]
        countI = endI - startI
        
        bars = []
        if cluster.bars:
            barsStartI = dichotomy.nearest_index(spikesX[0], [b.x for b in cluster.bars])
            barsEndI = dichotomy.nearest_index(spikesX[-1], [b.x for b in cluster.bars])
            bars = cluster.bars[barsStartI:barsEndI]

        return SpikeCluster(startI, countI, spikesX, spikesY, bars), startI, endI
    
    def remove_range_x(cluster, xstart, xend):
        startI = dichotomy.nearest_index(xstart, cluster.spikesX)
        endI = dichotomy.nearest_index(xend, cluster.spikesX) + 1
        left = SpikeCluster(0, startI - 1, cluster.spikesX[:startI], cluster.spikesY[:startI], [])
        right = SpikeCluster(endI, len(cluster.spikesY) - endI, cluster.spikesX[endI:], cluster.spikesY[endI:], [])
        return cluster.merge([left, right])

    def truncate_range_x(cluster, xstart, xend):
        startI = dichotomy.nearest_index(xstart, cluster.spikesX)
        endI = dichotomy.nearest_index(xend, cluster.spikesX) + 1
        return SpikeCluster.truncate_range_index(cluster, startI, endI)
    
    def truncate_range_index(cluster, startI, endI):
        spikesX = cluster.spikesX[startI:endI+1]
        spikesY = cluster.spikesY[startI:endI+1]
        countI = endI - startI + 1

        bars = []
        if cluster.bars:
            barsStartI = dichotomy.nearest_index(spikesX[0], [b.x for b in cluster.bars])
            barsEndI = dichotomy.nearest_index(spikesX[-1], [b.x for b in cluster.bars]) + 1
            bars = cluster.bars[barsStartI:barsEndI]

        return SpikeCluster(startI, countI, spikesX, spikesY, bars), startI, endI