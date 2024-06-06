import numpy as np

from SpikeCluster import *

class CurveUtils:
    def moving_average(data, window_size):
        if window_size == 0:
            return data.copy()
        return np.convolve(data, np.ones(window_size)/window_size, mode='same')
    
    def average_cluster(spikeCluster, window_size):
        spikesX = spikeCluster.spikesX.copy()
        spikesY = CurveUtils.moving_average(spikeCluster.spikesY, window_size)
        return SpikeCluster(spikeCluster.startI, spikeCluster.countI, spikesX, spikesY, spikeCluster.bars.copy())
