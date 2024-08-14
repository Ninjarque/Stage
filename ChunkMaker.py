from SpikeCluster import *
from AverageManager import *
from Bar import *
from AverageManager import *

class ChunkMaker:
    @staticmethod
    def make_default(datax, datay):
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

        for i in range(len(datax)):
            line = line.strip()
            if not line:
                print("empty line...")
                continue
            values = line.split(",")

            x = float(datax[i])
            y = float(datay[i])
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

        #print(final_x)

        final_avg_y = y_total / count
        #print("final avg on y = {}".format(final_avg_y))

        #final_y = [gy * final_avg_y for gy in final_y]

        return spikesData#final_x, final_y
    
    @staticmethod
    def make_splits(datax, datay, splits, precision):
        spikesData = []

        datax, datay = AverageManager.interpolate_with_precision(datax, datay, precision)

        startI = 0
        for i in range(splits):
            endI = int(len(datax) / splits * (i + 1))

            min_y = datay[endI]

            cluster = None
            if i == splits - 1:
                cluster = SpikeCluster(startI, len(datax) - startI, datax[startI:], datay[startI:], [])

            left_i = endI - 1
            right_i = endI + 1
            left_y = datay[left_i]
            right_y = datay[right_i]
            while left_y < min_y and left_y < right_y:
                left_i = left_i - 1
                endI = left_i + 1
                right_i = left_i + 2
                left_y = datay[left_i]
                min_y = datay[endI]
                right_y = datay[right_i]
                if left_i == startI:
                    endI = startI
                    break
            while right_y < min_y and left_y > right_y:
                right_i = right_i + 1
                endI = right_i + 1
                left_i = right_i - 2
                left_y = datay[left_i]
                min_y = datay[endI]
                right_y = datay[right_i]
                if right_i == len(datax) - 1:
                    break
            
            if left_i != startI:
                cluster = SpikeCluster(startI, endI - startI, datax[startI:endI], datay[startI:endI], [])

            if cluster is not None:
                spikesData.append(cluster)

            startI = endI

        return spikesData

    @staticmethod
    def compute_spikes_cluster_len(spikeCluster):
        return spikeCluster.spikesX[-1] - spikeCluster.spikesX[0]


    @staticmethod
    def make_reccursive_splits(datax, datay, splits_per_iterations, total_splits, precision):
        spikesData = ChunkMaker.make_splits(datax, datay, splits_per_iterations, precision)
        spikesToIterateOn = spikesData.copy()
        spikesToIterateOn.sort(key=ChunkMaker.compute_spikes_cluster_len, reverse=True)
        while len(spikesData) < total_splits:
            if len(spikesToIterateOn) == 0:
                break
            spike = spikesToIterateOn.pop(index=0)
            newSplits = ChunkMaker.make_splits(spike.spikesX, spike.spikesY, splits_per_iterations, precision)
            if len(newSplits) > 1:
                for i in range(len(newSplits)):
                    spikesToIterateOn.append(newSplits[i])
                spikesToIterateOn.sort(key=ChunkMaker.compute_spikes_cluster_len, reverse=True)
            elif len(newSplits) == 1:
                spikesData.append(newSplits[0])
        
        return spikesData
