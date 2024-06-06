import matplotlib.pyplot as plt
import numpy as np

from SpikeCluster import *
from AverageManager import *

X_SPACING_RATIO_BEFORE_SPLIT = 1.5

def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size)/window_size, mode='same')

def diff_ratio(r1, r2):
    return abs(r1 - r2) / (r1 + r2)

class SplitTree:
    def __init__(self, left=None, right=None, range=(0, -1), offset=0):
        self.left = left
        self.right = right
        self.range = range
        self.offset = offset

    def has_child(self):
        if self.left and self.right:
            return True
        return False
    
    def compute_span_ratio(node, total_length):
        range_max = node.range[1]
        range_min = node.range[0]
        if range_max == -1:
            range_max = total_length - 1
        return (range_max - range_min + 1) / total_length
    
    def should_prune_child(self, prune_below_ratio = 0.25):
        if not self.has_child():
            return False, self
        self_min = self.range[0]
        self_max = self.range[1]

        left_min = self.left.range[0]
        left_max = self.left.range[1]

        right_min = self.right.range[0]
        right_max = self.right.range[1]

        left_ratio = (left_max - left_min + 1) / (self_max - self_min + 1)
        right_ratio = (right_max - right_min + 1) / (self_max - self_min + 1)
        left_right = 1 - abs(left_ratio - right_ratio) / (left_ratio + right_ratio)
        if left_right < prune_below_ratio:
            if left_ratio > right_ratio:
                return True, self.left
            else:
                return True, self.right
        return False, self
    
    def prune(self, prune_below_ratio = 0.25):
        should_prune, t = self.should_prune_child(prune_below_ratio)
        while should_prune:
            print("Pruned tree because it had a split with less than", prune_below_ratio * 100, "%% of values in it!")
            should_prune, t = t.should_prune_child(prune_below_ratio)
        return t
    
    def length(self):
        if not self.has_child():
            return 1
        return self.left.length() + self.right.length()
    
    def show(self, curvex, curvey):
        splits = self.get_splits()
        plt.suptitle('Showing tree with {} splits'.format(len(splits)))
        c = 0
        plt.plot(curvex, curvey, '--')
        colors = ['r-', 'b-']
        for split in splits:
            cx = curvex[split[0]:split[1] + 1]
            cy = curvey[split[0]:split[1] + 1]
            plt.plot(cx, cy, colors[c])
            c = np.mod(c + 1, len(colors))
        plt.show()

    def get_splits(self, offset = 0):
        if not self.has_child():
            return [(self.range[0] + offset + self.offset, self.range[1] + offset + self.offset)]
        sl = self.left.get_splits(offset)
        sr = self.right.get_splits(offset)
        return sl + sr

class Splitter:
    def __init__(self):
        pass

    '''
    def get_splits(curvex, curvey):
        splits = []
        lst_start = 0
        splits_count = 0

        for x in range(2, len(curvex)):
            lst_dtx = curvex[x - 1] - curvex[x - 2]
            curr_dtx = curvex[x] - curvex[x - 1]
            if curr_dtx > lst_dtx * X_SPACING_RATIO_BEFORE_SPLIT:
                splits_count += 1
                splits.append((lst_start, x - 1))
                lst_start = x
        splits.append((lst_start, len(curvex) - 1))
        splits_count += 1
        return splits_count, splits
    '''
    def get_splits(curvex, curvey):
        splits = []
        lst_start = -1
        splits_count = 0

        for i in range(len(curvey)):
            if curvey[i] > 0:
                if lst_start == -1:
                    lst_start = i
            else:
                if lst_start != -1:
                    splits_count += 1
                    splits.append((lst_start, i - 1))
                    lst_start = -1
        
        # Add the last segment if it goes till the end and is above zero
        if lst_start != -1:
            splits.append((lst_start, len(curvex) - 1))
            splits_count += 1
        #print("get splits:", splits)
        return splits_count, splits

    def apply_threshold(curvex, curvey, threshold):
        cx = []
        cy = []
        for i in range(len(curvey)):
            cx.append(curvex[i])
            if curvey[i] > threshold:
                cy.append(curvey[i])
            else:
                cy.append(0)
        return cx, cy

    def try_split(curvex, curvey):
        maxy = max(curvey)
        miny = min(curvey)
        center = (maxy + miny) / 2.0

        #cx, cy = Splitter.apply_threshold(curvex, curvey, center)
        #splits_count, splits = Splitter.get_splits(cx, cy)
        splits_count = 0
        
        i = 0
        #plt.suptitle('i:{}, splits:{}, Trying split threshold [{},{}] {}'.format(i, splits_count, int(100 * maxy) / 100, int(100 * miny) / 100, int(100 * center) / 100))
        #plt.plot(curvex, curvey, 'r-')
        #plt.plot(cx, cy, 'b-')
        #plt.show()
        tries = 100

        while splits_count != 2 and i < tries:
            y = i / tries * (maxy - miny) + miny
            cx, cy = Splitter.apply_threshold(curvex, curvey, y)
            splits_count, splits = Splitter.get_splits(cx, cy)
            #plt.suptitle('i:{}, splits ({}) Trying curve [{},{}] {}'.format(i, splits_count, int(100 * maxy) / 100, int(100 * miny) / 100, int(100 *  y) / 100))
            #plt.plot(curvex, curvey, 'r-')
            #plt.plot(cx, cy, 'b-')
            #plt.show()

            i += 1

        if i >= tries:
            #print("failed to split")
            return False, splits
        '''
        lst_center = -1
        while splits_count != 2:
            if splits_count > 2:
                maxy = center
            else:
                miny = center
            center = (maxy + miny) / 2.0
            if int(10 * center) == int(10 * lst_center) or i >= 50:
                plt.suptitle('Could not find splits for curve [{},{}] {}'.format(i, splits_count, int(100 * maxy) / 100, int(100 * miny) / 100, int(100 * center) / 100))
                plt.plot(curvex, curvey, 'r-')
                plt.plot(cx, cy, 'b-')
                plt.show()
                return False, (0, len(curvex) - 1)
            cx, cy = Splitter.apply_threshold(curvex, curvey, center)
            splits_count, splits = Splitter.get_splits(cx, cy)
            lst_center = center
            i += 1
            #plt.suptitle('i:{}, splits:{}, Trying split threshold [{},{}] {}'.format(i, splits_count, int(100 * maxy) / 100, int(100 * miny) / 100, int(100 * center) / 100))
            #plt.plot(curvex, curvey, 'r-')
            #plt.plot(cx, cy, 'b-')
            #plt.show()
        '''
            
        return True, splits
    
    def generate_tree(curvex, curvey, average_smoothing_ratio=0.1, prune_below_ratio = 0.0, offset = 0):
        avg_curvey = curvey
        window_size = int(len(curvex) * average_smoothing_ratio)
        if window_size > 0:
            window_size = int(len(curvex) * average_smoothing_ratio)
            avg_curvey = moving_average(curvey, window_size)
        

        #plt.suptitle('Generating tree of [{},{}]'.format(0, len(curvex)))
        #plt.plot(curvex, curvey, 'r-')
        #plt.show()

        can_split, splits = Splitter.try_split(curvex, avg_curvey)

        if not can_split:
            #print("offset:", offset)
            return SplitTree(range=(0, len(curvex) - 1), offset=offset)

        left_split = splits[0]
        right_split = splits[1]
        #print("left")
        left_tree = Splitter.generate_tree(curvex[left_split[0]:left_split[1]+1], curvey[left_split[0]:left_split[1]+1], average_smoothing_ratio, offset=offset + left_split[0])
        #print("right")
        right_tree = Splitter.generate_tree(curvex[right_split[0]:right_split[1]+1], curvey[right_split[0]:right_split[1]+1], average_smoothing_ratio, offset=offset + right_split[0])

        tree = SplitTree(left=left_tree, right=right_tree, range=(0, len(curvex) - 1), offset=offset)
        return tree.prune(prune_below_ratio)
    
    '''
    def match_trees(target_tree, current_tree, target_length, current_length, prune_ratio = 0.25, diff_span_ratio_threshold = 0.2):
        target_tree = target_tree.prune(prune_ratio)
        current_tree = current_tree.prune(prune_ratio)

        target_span_ratio = target_tree.compute_span_ratio(target_length)
        current_span_ratio = current_tree.compute_span_ratio(current_length)

        smallest, biggest = target_tree, current_tree
        smallest_span_ratio, biggest_span_ratio = target_span_ratio, current_span_ratio
        if target_span_ratio > current_span_ratio:
            smallest, biggest = current_tree, target_tree
            smallest_span_ratio, biggest_span_ratio = current_span_ratio, target_span_ratio

        while diff_ratio(smallest_span_ratio, biggest_span_ratio) > diff_span_ratio_threshold:
            break

        pass
    '''