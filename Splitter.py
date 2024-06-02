from SpikeCluster import *
from AverageManager import *

X_SPACING_RATIO_BEFORE_SPLIT = 1.5

class SplitTree:
    def __init__(self, left=None, right=None, range=(0, -1)):
        self.left = left
        self.right = right
        self.range = range

class Splitter:
    def __init__(self):
        pass

    def get_splits(curvex, curvey):
        splits = []
        lst_start = 0
        splits_counts = 0

        for x in range(2, len(curvex)):
            lst_dtx = curvex[x - 1] - curvex[x - 2]
            curr_dtx = curvex[x] - curvex[x - 1]
            if curr_dtx > lst_dtx * X_SPACING_RATIO_BEFORE_SPLIT:
                splits_count += 1
                splits.append((lst_start, x - 1))
                lst_start = x
        splits.append((lst_start, len(curvex) - 1))
        return splits_count, splits

    def apply_threshold(curvex, curvey, threshold):
        cx = []
        cy = []
        for i in range(len(curvey)):
            y = curvey[i]
            if y > threshold:
                cx.append(curvex[i])
                cy.append(curvey[i])
        return cx, cy

    def try_split(self, curvex, curvey, bars):
        maxy = max(curvey)
        miny = min(curvey)
        center = (maxy + miny) / 2.0

        splits_count, splits = Splitter.get_splits(curvex, curvey)

        while splits_count != 2:
            if splits_count > 2:
                maxy = center
            else:
                miny = center
            center = (maxy + miny) / 2.0
            cx, cy = Splitter.apply_threshold(curvex, curvey, center)
            splits_count, splits = Splitter.get_splits(cx, cy)

        return True, splits