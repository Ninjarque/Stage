import math
import numpy as np

import dichotomy
from SpikeCluster import *
from Bar import *
from AverageManager import *

XY_NOISE_Y_THRESHOLD = 0.0001
XY_GROUP_START_Y_THRESHOLD = 0.0
XY_GROUP_LEAVE_Y_THRESHOLD = 0.01

XY_OUT_OF_GROUP_X_OFFSET = 0.007

DPT_NOISE_Y_THRESHOLD = 0.035 #0.035 #0.03
DPT_GROUP_START_Y_THRESHOLD = 0.07
DPT_GROUP_LEAVE_Y_THRESHOLD = 0.04

DPT_OUT_OF_GROUP_X_OFFSET = 0.005 #0.01

SMOOTH_AVERAGE_MAX_CONTEXT_SIZE = 1000 #2000 #1000
AVERAGE_PREDICTION_CONTEXT_SIZE_PERCENTAGE = 0.01 #0.001

AVERAGE_PREDICTION_GROUP_SMOOTHING_PERCENTAGE = 0.001 #0.001


SPIKE_TREE_MAX_CLUSTERS_COUNT = 10        

class SpikeTree:
    less = None
    more = None
    targetValue = 0
    targetProperty = ""

    spikeClusters = []

    _splitVoteImin = 1000000000
    _splitVoteImax = 0
    _splitVoteXmin = 1000000000
    _splitVoteXmax = 0
    _splitVoteYmin = 1000000000
    _splitVoteYmax = 0

    def __init__(self, targetValue, targetProperty, lessThanTree, moreThanTree):
        self.targetValue = targetValue
        self.targetProperty = targetProperty
        self.less = lessThanTree
        self.more = moreThanTree
    def __init__(self, spikeClusters):
        self.spikeClusters = spikeClusters
        self.less = None
        self.more = None

    def hasChilds(self):
        return self.less == None or self.more == None
    
    def isPropertyLessThanTarget(cluster, relativeMargin, targetValue, targetProperty):
        s = 1
        if relativeMargin < 0:
            s = -1
        if targetProperty == "i":
            mi = [i for i in cluster.bars if i.i * s < targetValue * s + relativeMargin]
            return len(mi) > 0
        if targetProperty == "x":
            mx = [x for x in cluster.bars if x.x < targetValue]
            return len(mx) > 0
        if targetProperty == "y":
            my = [y for y in cluster.bars if y.y < targetValue]
            return len(my) > 0
        return True

    def updateSplitVote(self, cluster):
        self._splitVoteImax = max(self._splitVoteImax, cluster.startI)
        self._splitVoteImin = min(self._splitVoteImin, cluster.startI)
        self._splitVoteXmax = max(self._splitVoteXmax, max(cluster.spikesX))
        self._splitVoteXmin = min(self._splitVoteXmin, min(cluster.spikesX))
        self._splitVoteYmax = max(self._splitVoteYmax, max(cluster.spikesY))
        self._splitVoteYmin = min(self._splitVoteYmin, min(cluster.spikesY))

    def append(self, cluster):
        '''
        if self.hasChilds():
            if isPropertyLessThanTarget(cluster, self.targetValue, self.targetProperty):
                less.append(cluster)
            else:
                more.append(cluster)
        else:
            spikeClusters.append(cluster)
        '''



def smooth_average(x, outX, lstAvg, sampling):
    if sampling == 0:
        return x
    return lstAvg + 1.0/sampling * (x - outX)

def smooth_average1(x, outX, lstAvg, sampling):
    if sampling == 0:
        return x
    return lstAvg + 1.0/sampling * (x - lstAvg)

#fichier permettant d'attribuer un identifiant aux spikes
def parse_ASG(filename):
    if not filename:
        print("Empty path, proceeding with default one")
        filename = "../Exemple_1/aj00.asg"
    filename = filename.strip("\" ")
    file1 = open(filename, 'r')
    lines = file1.readlines()
    count = 0

    bars = []

    for line in lines:
        count += 1
        line = line.strip()
        if not line:
            #print("empty line...")
            continue
        values = line.split()
        
        i = 0
        x = 0
        vA = 0
        vB = 0
        vC = 0

        id = []
        lineLen = len(values)
        if lineLen == 5:
            i = int(values[0])
            x = float(values[1])
            vA = float(values[2])
            vB = float(values[3])
            vC = float(values[4])
        elif lineLen >= 12:
            i = int(values[0])
            x = float(values[1])
            vA = float(values[3])
            vB = float(values[4])
            vC = float(values[5])
            id = [v.strip("'\" ") for v in values[6:]]
        
        #print("Line{}:   \ti({}), at x = {}, vA = {}, vB = {}, vC = {}, id = {}".format(count, i, x, vA, vB, vC, id))
        bars.append(Bar(i, x, 1.0, id))
    file1.close()
    return bars

#fichier simul pour l'attribuer d'un identifiant aux spikes
def parse_T(filename):
    if not filename:
        print("Empty path, proceeding with default one")
        filename = "../Exemple_1/spectr.t"
    filename = filename.strip("\" ")
    file1 = open(filename, 'r')
    lines = file1.readlines()
    count = 0

    bars = []

    found_values = False

    nb = 0

    for line in lines:
        count += 1
        line = line.strip()
        if not line:
            #print("empty line...")
            continue
        line = line.strip()

        values = line.split()
        
        if not found_values and values[0] == "Frequency" and len(values) > 1:
            found_values = True
            continue
        elif not found_values:
            continue
        if found_values and values[0] == "Number":
            found_values = False
            continue

        i = 0
        x = 0
        vA = 0
        vB = 0
        vC = 0

        #print(line)

        id = []
        lineLen = len(values)
        i = nb
        x = float(values[0])
        v = float(values[1])
        vA = values[3]
        vB = values[4]
        vC = values[5]

        vD = values[8]
        vE = values[9]
        vF = values[10]

        id = [vA, vB, vC, vD, vE, vF]
        
        #print("Line{}:   \ti({}), at x = {}, vA = {}, vB = {}, vC = {}, id = {}".format(count, i, x, vA, vB, vC, id))
        bars.append(Bar(i, x, v, id))
        nb += 1
    file1.close()
    return bars
    
"""
def parse_XY(filename):
    if not filename:
        print("Empty path, proceeding with default one")
        filename = "../Exemple_1/simul.xy"
    filename = filename.strip("\" ")
    file1 = open(filename, 'r')
    lines = file1.readlines()

    y_total = 0.0
    count = 0

    group_x = []
    group_y = []

    spikesData = []

    groupStart = 0
    inGroup = False
    wasInGroup = False

    for line in lines:
        line = line.strip()
        if not line:
            print("empty line...")
            continue
        values = line.split()
        x = float(values[0])
        y = float(values[1])

        if abs(y) < XY_NOISE_Y_THRESHOLD:
            inGroup = False
        elif not inGroup:
            inGroup = True
            groupStart = count
        count += 1
        y_total += y

        if wasInGroup != inGroup:
            spikesData.append(SpikeCluster(groupStart, count - groupStart, group_x, group_y))
            group_x = []
            group_y = []

        group_x.append(x)
        group_y.append(y)

        wasInGroup = inGroup

    file1.close()
    return spikesData
"""
def parse_XY(filename):
    if not filename:
        print("Empty path, proceeding with default one")
        filename = "../Exemple_1/simul.xy"
    filename = filename.strip("\" ")
    file1 = open(filename, 'r')
    lines = file1.readlines()

    y_total = 0.0
    count = 0
    real_count = 0

    grouping = False
    groupStart = 0
    outOfGroupFor = 0
    outOfGroupSince = -1

    final_x = []
    final_y = []

    group_x = []
    group_y = []
    group_maxima_i = []

    lstX = 0
    lstY = 0

    avg_y = 0.0
    lst_avg_y = 0.0
    avg_derivative = 0.0

    spikesData = []

    groups = 0

    avg_y_manager = AverageManager(SMOOTH_AVERAGE_MAX_CONTEXT_SIZE)
    local_avg_y_manager = AverageManager(int(SMOOTH_AVERAGE_MAX_CONTEXT_SIZE * AVERAGE_PREDICTION_CONTEXT_SIZE_PERCENTAGE))

    lstTY = 0
    startingLocalMaxima = False

    print("starting 'parse_XY' process...")

    for line in lines:
        line = line.strip()
        if not line:
            print("empty line...")
            continue
        values = line.split()

        x = float(values[0])
        y = float(values[1])
        real_y = y

        y_total += y

        avg_y = avg_y_manager.compute(y)
        local_avg_y = local_avg_y_manager.compute(y)

        avg_derivative = (local_avg_y - lst_avg_y) / (x - lstX)
        avg_prediction = avg_derivative * SMOOTH_AVERAGE_MAX_CONTEXT_SIZE * AVERAGE_PREDICTION_CONTEXT_SIZE_PERCENTAGE + local_avg_y

        ty = 0.0
        if avg_y != 0.0:
            ty = local_avg_y / abs(avg_y)
        if ty <= 0.0:
            ty = 0.0

        maximaTY = 0
        if lstTY < ty and avg_derivative > 0.02:
            startingLocalMaxima = True
        if startingLocalMaxima and lstTY >= ty and avg_derivative < -0.02:
            startingLocalMaxima = False
            maximaTY = y

        if ty + avg_prediction * AVERAGE_PREDICTION_GROUP_SMOOTHING_PERCENTAGE >= 1 + XY_GROUP_START_Y_THRESHOLD:
            if not grouping:
                spikesData.append(SpikeCluster(groupStart, outOfGroupSince - groupStart, group_x, group_y, group_maxima_i))
                groups += 1
                group_x = []
                group_y = []
                group_maxima_i = []
            grouping = True
            groupStart = real_count
            outOfGroupFor = 0
            outOfGroupSince = -1

        if ty < 1 + XY_NOISE_Y_THRESHOLD or (grouping and ty < 1 + XY_GROUP_LEAVE_Y_THRESHOLD + avg_prediction * AVERAGE_PREDICTION_GROUP_SMOOTHING_PERCENTAGE):
            if grouping and outOfGroupSince == -1:
                outOfGroupSince = real_count
            if grouping and outOfGroupFor < XY_OUT_OF_GROUP_X_OFFSET:
                outOfGroupFor += x - lstX
            elif grouping and outOfGroupFor >= XY_OUT_OF_GROUP_X_OFFSET:
                grouping = False
                spikesData.append(SpikeCluster(groupStart, outOfGroupSince - groupStart, group_x, group_y, group_maxima_i))
                groups += 1
                group_x = []
                group_y = []
                group_maxima_i = []
            else:
                ty = 0.0
                y = 0.0

        if maximaTY != 0:
            group_maxima_i.append(Bar(real_count - groupStart - 1, lstX, lstY))
        
        lst_avg_y = local_avg_y
        real_count += 1
        count += 1
        group_x.append(x)
        group_y.append(real_y)

        lstX = x
        lstY = y
        lstTY = ty
    
    if len(group_x) > 0:
        spikesData.append(SpikeCluster(groupStart, outOfGroupSince - groupStart, group_x, group_y, group_maxima_i))

    file1.close()

    final_avg_y = y_total / count

    return spikesData

def parse_DPT(filename):
    if not filename:
        print("Empty path, proceeding with default one")
        filename = "../Exemple_1/Nu3 SiF4 160K 0.14mb 51mm Cal.dpt"
    filename = filename.strip("\" ")
    file1 = open(filename, 'r')
    lines = file1.readlines()

    y_total = 0.0
    count = 0
    real_count = 0

    grouping = False
    groupStart = 0
    outOfGroupFor = 0
    outOfGroupSince = -1

    final_x = []
    final_y = []

    group_x = []
    group_y = []
    group_maxima_i = []

    lstX = 0
    lstY = 0

    avg_y = 0.0
    lst_avg_y = 0.0
    avg_derivative = 0.0
    #avg_y1 = 0.0

    spikesData = []

    groups = 0

    avg_y_manager = AverageManager(SMOOTH_AVERAGE_MAX_CONTEXT_SIZE)
    local_avg_y_manager = AverageManager(int(SMOOTH_AVERAGE_MAX_CONTEXT_SIZE * AVERAGE_PREDICTION_CONTEXT_SIZE_PERCENTAGE))

    lstTY = 0
    startingLocalMaxima = False

    print("starting 'parse_DPT' process...")

    for line in lines:
        line = line.strip()
        if not line:
            print("empty line...")
            continue
        values = line.split(",")

        x = float(values[0])
        y = float(values[1])
        real_y = y

        y_total += y

        #avg_y = smooth_average(y, out_y, avg_y, min(real_count, SMOOTH_AVERAGE_MAX_CONTEXT_SIZE))
        #avg_y1 = smooth_average1(y, out_y, avg_y1, min(real_count, SMOOTH_AVERAGE_MAX_CONTEXT_SIZE))
        
        avg_y = avg_y_manager.compute(y)
        local_avg_y = local_avg_y_manager.compute(y)

        #the average's derivative can tell us how is the average evolving at each point
        #making it easier to figure out if a point should really be seen as under average
        avg_derivative = (local_avg_y - lst_avg_y) / (x - lstX)
        #print("avg derivative {}".format(avg_derivative))
        avg_prediction = avg_derivative * SMOOTH_AVERAGE_MAX_CONTEXT_SIZE * AVERAGE_PREDICTION_CONTEXT_SIZE_PERCENTAGE + local_avg_y
        #print("avg prediction {} in {}".format(avg_prediction, SMOOTH_AVERAGE_MAX_CONTEXT_SIZE * AVERAGE_PREDICTION_CONTEXT_SIZE_PERCENTAGE))

        #print("current avg {}, MY avg = {}".format(y/avg_y, y/avg_y1))

        ty = local_avg_y / abs(avg_y)
        #print(ty)
        if ty <= 0.0:
            ty = 0.0

        maximaTY = 0
        if lstTY < ty and avg_derivative > 0.02:
            startingLocalMaxima = True
        if startingLocalMaxima and lstTY >= ty and avg_derivative < -0.02:
            startingLocalMaxima = False
            maximaTY = y

        if ty + avg_prediction * AVERAGE_PREDICTION_GROUP_SMOOTHING_PERCENTAGE >= 1 + DPT_GROUP_START_Y_THRESHOLD:#abs(ty) >= DPT_GROUP_START_Y_THRESHOLD:
            grouping = True
            groupStart = real_count
            outOfGroupFor = 0
            outOfGroupSince = -1

        if ty < 1 + DPT_NOISE_Y_THRESHOLD or (grouping and ty < 1 + DPT_GROUP_LEAVE_Y_THRESHOLD + avg_prediction * AVERAGE_PREDICTION_GROUP_SMOOTHING_PERCENTAGE):#abs(ty) < DPT_NOISE_Y_THRESHOLD:
            if grouping and outOfGroupSince == -1:
                outOfGroupSince = real_count
            if grouping and outOfGroupFor < DPT_OUT_OF_GROUP_X_OFFSET:
                #consider there might be other spikes in group
                outOfGroupFor += x - lstX
            elif grouping and outOfGroupFor >= DPT_OUT_OF_GROUP_X_OFFSET:
                #out of group for too long, grouping what has been found
                grouping = False

                spikesData.append(SpikeCluster(groupStart, outOfGroupSince - groupStart, group_x, group_y, group_maxima_i))
                
                groups += 1

                group_x = []
                group_y = []
                group_maxima_i = []
            else:
                #not grouping, value is useless
                ty = 0.0
                y = 0.0

        #offset of 1 because the maxima is detected upon leaving the peak, therefore it has to be prior to detection
        if maximaTY != 0:
            group_maxima_i.append(Bar(real_count - groupStart - 1, lstX, lstY))
        
        lst_avg_y = local_avg_y
        real_count += 1
        count += 1
        group_x.append(x)
        #v = max(y * local_avg_y, 0.0)
        #group_y.append(math.sqrt(v)) #group_y.append(ty)
        
        group_y.append(real_y)

        lstX = x
        lstY = y
        lstTY = ty
    
    if len(group_x) > 0:
        #[final_x.append(gx) for gx in group_x[:outOfGroupSince]]
        #[final_y.append(gy) for gy in group_y[:outOfGroupSince]]
        spikesData.append(SpikeCluster(groupStart, outOfGroupSince - groupStart, group_x, group_y, group_maxima_i))

        #print("made group of {}".format(real_count - outOfGroupSince))

    file1.close()
    #print(final_x)

    final_avg_y = y_total / count
    #print("final avg on y = {}".format(final_avg_y))

    #final_y = [gy * final_avg_y for gy in final_y]

    return spikesData#final_x, final_y

def compile_DPT(filename, spikesData):
    if not filename:
        print("Empty path, proceeding with default one")
        filename = "../Exemple_1/Reconstructed.dpt"
    filename = filename.strip("\" ")
    file1 = open(filename, 'w')
    for spikeCluster in spikesData:
        for x, y in zip(spikeCluster.spikesX, spikeCluster.spikesY):
            file1.write("{},{}\n".format(x, y))

    file1.close()

def graph_DPT(spikesData):
    xs = []
    ys = []
    for spikeCluster in spikesData:
        for x, y in zip(spikeCluster.spikesX, spikeCluster.spikesY):
            xs.append(x)
            ys.append(y)

    return xs, ys