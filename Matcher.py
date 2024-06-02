from SpikeCluster import *
from AverageManager import *

import MatchCandidatesGenerator

class MatchingStep:
    def __init__(self, featureExtractor, stepSlidingPrecision, stepChunkPrecision, stepRangePrecision):
        self.featureExtractor = featureExtractor
        self.stepSlindingPrecision = stepSlidingPrecision
        self.stepChunkPrecision = stepChunkPrecision
        self.stepRangePrecision = stepRangePrecision

class Matcher:
    def __init__(self, *matchingSteps):
        self.matchingSteps = matchingSteps

    def match(self, target_chunk, current_chunk, reccursions = 1):
        target_start = 0
        target_end = -1
        current_start = 0
        current_end = -1

        real_target_offset = 0
        real_target_end = 0

        for r in range(reccursions):
            #as of now, every reccursion doesn't change squat about the previous ones
            #first we'll need to change the precision over reccursions -> somewhat done, but target_start (and maybe end) error, seems like set to 0, needs to accumulate maybe
            #then we'll
            target_start, target_end, x_start, x_end = self.match_chunk(target_chunk, current_chunk)
            
            real_target_offset += target_start
            real_target_start = target_start
            real_target_end = target_end
            
            target_chunk, target_start, target_end = SpikeCluster.truncate_range_index(target_chunk, target_start, target_end)
            
            real_target_offset += target_start
            real_target_start = target_start
            real_target_end = target_end

            current_chunk, current_start, current_end = SpikeCluster.truncate_range_x(current_chunk, x_start, x_end)

            if r < reccursions - 1:
                target_chunk, target_start, target_end = SpikeCluster.truncate(target_chunk, 0.5)
                
                real_target_offset += target_start
                real_target_start = target_start
                real_target_end = target_end

                current_chunk, current_start, current_end = SpikeCluster.truncate(current_chunk, 0.5)

        return real_target_offset + real_target_start, real_target_offset + real_target_end, current_chunk.spikesX[0], current_chunk.spikesX[-1]

    def match_chunk(self, target_chunk, current_chunk):
        target_start, target_end = 0, -1
        x_start_offset, x_end_offset = 0, -1
        x_start, x_end = 0, 0
        bestMatch = 0
        step = 0
        for matchingStep in self.matchingSteps:
            print("#### Matcher, step", step, "####")
            featureExtractor = matchingStep.featureExtractor
            stepSlindingPrecision = matchingStep.stepSlindingPrecision
            stepChunkPrecision = matchingStep.stepChunkPrecision
            stepRangePrecision = matchingStep.stepRangePrecision
            target_start, target_end, x_start_offset, x_end_offset = featureExtractor.match(target_chunk.spikesX, target_chunk.spikesY, current_chunk.spikesX, current_chunk.spikesY, stepSlindingPrecision)

            m_range = min((target_chunk.spikesX[-1] - target_chunk.spikesX[0]), (current_chunk.spikesX[-1] - current_chunk.spikesX[0]))
            xvalues = m_range / 2.0 * (1 - stepRangePrecision)
            x_start = current_chunk.spikesX[0] - xvalues
            x_end = current_chunk.spikesX[-1] + xvalues

            x_start = ((current_chunk.spikesX[x_start_offset]) * stepRangePrecision) + (x_start * (1.0 - stepRangePrecision))
            x_end = ((current_chunk.spikesX[x_end_offset]) * stepRangePrecision) + (x_end * (1.0 - stepRangePrecision))

            current_chunk = SpikeCluster.truncate_range_x(current_chunk, x_start, x_end)

            step += 1


        return target_start, target_end, x_start, x_end