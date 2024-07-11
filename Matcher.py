from SpikeCluster import *
from AverageManager import *
from Splitter import *

from CurveUtils import *

import MatchCandidatesGenerator

TRUNCATE_PERCENTAGE_PER_ITERATION = 0.05 #0.2

class MatchingStep:
    def __init__(self, featureExtractor, stepSlidingPrecision, stepRangePrecision):
        self.featureExtractor = featureExtractor
        self.stepSlindingPrecision = stepSlidingPrecision
        self.stepRangePrecision = stepRangePrecision

class Matcher:
    def __init__(self, *matchingSteps):
        self.matchingSteps = matchingSteps

    def match(self, target_chunk, current_chunk, reccursions = 1, average_window_start_ratio = 0.0, average_window_end_ratio = 0.0):
        target_start = 0
        target_end = -1
        current_start = 0
        current_end = -1

        real_target_offset = 0
        real_target_end = 0

        target_tree = SplitTree(range=(0, len(target_chunk.spikesX) - 1))
        current_tree = SplitTree(range=(0, len(current_chunk.spikesX) - 1))

        for r in range(reccursions):
            print("#### RECCURSION, step", r, "####")
            ratio = average_window_start_ratio
            if reccursions > 1:
                ratio = r / (reccursions - 1)
            average_ratio = average_window_start_ratio * (1 - ratio) + average_window_end_ratio * ratio
            target_window = int(len(target_chunk.spikesX) * average_ratio)
            current_window = int(len(current_chunk.spikesX) * average_ratio)
            #min_window = min(target_window, current_window)
            #target_window = min_window
            #current_window = min_window
            target_avg_chunk = CurveUtils.average_cluster(target_chunk, target_window)
            current_avg_chunk = CurveUtils.average_cluster(current_chunk, current_window)

            '''
            plt.suptitle('Averaged vs normal target at reccursion {}/{}, with window:{} given average ratio of {}'.format(r, reccursions - 1, target_window, average_ratio))
            plt.plot(target_chunk.spikesX, target_chunk.spikesY, 'r-')
            plt.plot(target_avg_chunk.spikesX, target_avg_chunk.spikesY, 'b-')
            plt.show()

            plt.suptitle('Averaged vs normal current at reccursion {}/{}, with window:{} given average ratio of {}'.format(r, reccursions - 1, current_window, average_ratio))
            plt.plot(current_chunk.spikesX, current_chunk.spikesY, 'r-')
            plt.plot(current_avg_chunk.spikesX, current_avg_chunk.spikesY, 'b-')
            plt.show()
            '''

            target_start, target_end, x_start, x_end, match_dist = self.match_chunk(target_avg_chunk, current_avg_chunk)
            
            target_chunk, target_start, target_end = SpikeCluster.truncate_range_index(target_chunk, target_start, target_end)
            
            current_chunk, current_start, current_end = SpikeCluster.truncate_range_x(current_chunk, x_start, x_end)

            #Here is where we could split!
            target_tree = Splitter.generate_tree(target_chunk.spikesX, target_chunk.spikesY)
            current_tree = Splitter.generate_tree(current_chunk.spikesX, current_chunk.spikesY)

            if r < reccursions - 1:
                target_chunk, target_start, target_end = SpikeCluster.truncate(target_chunk, TRUNCATE_PERCENTAGE_PER_ITERATION)
                
                #real_target_offset += target_start
                #real_target_start = target_start
                #real_target_end = target_end

                current_chunk, current_start, current_end = SpikeCluster.truncate(current_chunk, TRUNCATE_PERCENTAGE_PER_ITERATION)

        #return real_target_offset + real_target_start, real_target_offset + real_target_end, current_chunk.spikesX[0], current_chunk.spikesX[-1]
        return target_chunk.spikesX[0], target_chunk.spikesX[-1], current_chunk.spikesX[0], current_chunk.spikesX[-1], target_tree, current_tree

    def match_chunk(self, target_chunk, current_chunk):
        target_start, target_end = 0, -1
        x_start_offset, x_end_offset = 0, -1
        x_start, x_end = 0, 0
        bestMatch = 0
        step = 0
        final_dist = 0
        for matchingStep in self.matchingSteps:
            print("#### Matcher, step", step, "####")
            featureExtractor = matchingStep.featureExtractor
            stepSlindingPrecision = matchingStep.stepSlindingPrecision
            stepRangePrecision = matchingStep.stepRangePrecision
            target_start, target_end, x_start_offset, x_end_offset, dist = featureExtractor.match(target_chunk.spikesX, target_chunk.spikesY, current_chunk.spikesX, current_chunk.spikesY, stepSlindingPrecision)

            #Here is something important... The way the final dist is computed, as of now, it will be a sum, but it could be more complicated
            final_dist += dist

            m_range = min((target_chunk.spikesX[-1] - target_chunk.spikesX[0]), (current_chunk.spikesX[-1] - current_chunk.spikesX[0]))
            xvalues = m_range / 2.0 * (1 - stepRangePrecision)
            x_start = current_chunk.spikesX[0] - xvalues
            x_end = current_chunk.spikesX[-1] + xvalues

            x_start = ((current_chunk.spikesX[x_start_offset]) * stepRangePrecision) + (x_start * (1.0 - stepRangePrecision))
            x_end = ((current_chunk.spikesX[x_end_offset]) * stepRangePrecision) + (x_end * (1.0 - stepRangePrecision))

            current_chunk, _, _ = SpikeCluster.truncate_range_x(current_chunk, x_start, x_end)

            step += 1


        return target_start, target_end, x_start, x_end, final_dist