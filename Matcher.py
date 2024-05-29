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

    def match(self, target_chunk, current_chunks):
        candidates = MatchCandidatesGenerator.generate(target_chunk, current_chunks)
        if not candidates:
            print("Couldn't find possible matches in current chunks!")
            return []
        candidates = [c for c in candidates if c.is_over_noise_threshold()]
        list_x = []
        list_y = []
        for candidate in candidates:
            #print("current_chunks_list", current_chunks_list)
            x = [v for v in candidate.spikesX]
            y = [v for v in candidate.spikesY]
            print("adding chunk [", x[0], ",", x[-1], "], size:", len(x))
            list_x.append(x)
            list_y.append(y)
            pass
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
            target_start, target_end, bestMatch, x_start_offset, x_end_offset = featureExtractor.match(target_chunk.spikesX, target_chunk.spikesY, list_x, list_y, stepSlindingPrecision)
            #this version of the algorithm could work if only it where to select a bigger range if ensure, we'll see later on about that
            #list_x = list_x[bestMatch][x_start_offset:x_end_offset]
            #list_y = list_y[bestMatch][x_start_offset:x_end_offset]
            #this version will do for now, altough, a little wasteful


            #WHAT ABOUT COMPUTING THE CHUNK SPAN BASED ON THE RANGE SCALING WITH DICHOTOMY (AGAIN XD)

            chunks = len(list_x) * (1 - stepChunkPrecision)
            bestMatchRangeMin = int(max(0, bestMatch - chunks))
            bestMatchRangeMax = int(min(len(list_x) - 1, bestMatch + chunks) + 1)
            print("next step ranges", bestMatchRangeMin, ":", bestMatchRangeMax)
            list_bestMatch_x = list_x[bestMatch]
            list_bestMatch_y = list_x[bestMatch]

            list_x = list_x[bestMatchRangeMin:bestMatchRangeMax]
            list_y = list_y[bestMatchRangeMin:bestMatchRangeMax]


            print("list size", len(list_x), ", match index", bestMatch)

            xvalues = (list_bestMatch_x[-1] - list_bestMatch_x[0]) / 2.0 * (1 - stepRangePrecision)
            x_start = list_bestMatch_x[0] - xvalues
            x_end = list_bestMatch_x[-1] + xvalues

            x_start = ((list_bestMatch_x[x_start_offset]) * stepRangePrecision) + (x_start * (1.0 - stepRangePrecision))
            x_end = ((list_bestMatch_x[x_end_offset]) * stepRangePrecision) + (x_end * (1.0 - stepRangePrecision))


            step += 1


        return target_start, target_end, x_start, x_end