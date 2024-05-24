import numpy as np

from filter import *


def _evaluateFilter(clusters, filter):
    v = 0
    for cluster in clusters:
        curvex = cluster.spikesX
        curvey = cluster.spikesY
        valid, _, _ = filter.apply(curvex, curvey)
        if valid:
            v += 1
    return v / len(clusters)

def RandomFilter(clusters, max_tries):
    clusterCnt = len(clusters)
    
    bestFilter = None
    bestFilterScore = 0

    while max_tries >= 0 or bestFilterScore == 1:
        func = np.random.normal(0, 1, clusterCnt)

        c = int(np.random.random() * clusterCnt)
        
        startX = clusters[c].spikesX[0]
        endX = clusters[c].spikesX[-1]


        filter = Filter(startX, endX, func)

        ratio = _evaluateFilter(clusters, filter)
        eval = 1.0 - abs(ratio - 0.5) * 2.0
        if not bestFilter or bestFilterScore < eval:
            bestFilter = filter
            bestFilterScore = eval

        max_tries -= 1
    print("Best random filter's function values are:", bestFilter.function_values)
    pass