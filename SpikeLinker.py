import numpy as np
import dichotomy

from Bar import *
from Splitter import *

OVERLAPING_BARS_THRESHOLD = 0.1

class SpikeLinker:
    def __init__(self):
        pass

    def get_bar_dist(bar1, bar2, bars1_x_offset, bars2_x_offset, bars1_span, bars2_span):
        if not bar1 or not bar2:
            return 100000
        return ((bar1.x - bars1_x_offset) / bars1_span - (bar2.x - bars2_x_offset) / bars2_span) * ((bar1.x - bars1_x_offset) / bars1_span - (bar2.x - bars2_x_offset) / bars2_span)
    
    def get_best_bar_match(bar1, bars2, bars1_x_offset, bars2_x_offset, bars1_span, bars2_span):
        best_index = -1
        best_dist = 100000

        b2i = 0
        for bar2 in bars2:
            dist = SpikeLinker.get_bar_dist(bar1, bar2, bars1_x_offset, bars2_x_offset, bars1_span, bars2_span)

            if dist < best_dist or best_index == -1:
                best_index = b2i
                best_dist = dist

            b2i += 1

        return best_index
    
    def get_bars_in_range(x_start, x_end, bars):
        start = 0
        while start < len(bars):
            if bars[start].x >= x_start:
                break
            start += 1
        end = len(bars) - 1
        while end > start:
            if bars[end].x <= x_end:
                break
            end -= 1
        return start, end
        

    def link(target_x_start, target_x_end, target_bars, current_x_start, current_x_end, current_bars):
        target_start, target_end = SpikeLinker.get_bars_in_range(target_x_start, target_x_end, target_bars)
        target_bars = target_bars[target_start:target_end+1]
        
        current_start, current_end = SpikeLinker.get_bars_in_range(current_x_start, current_x_end, current_bars)
        current_bars = current_bars[current_start:current_end+1]

        # Determine which list is shorter and use it as the target list
        if len(target_bars) > len(current_bars):
            target_bars, current_bars = current_bars, target_bars
            target_x_start, current_x_start = current_x_start, target_x_start
            target_x_end, current_x_end = current_x_end, target_x_end

        
        print("len target bars", len(target_bars), "len current bars", len(current_bars))

        bars1_span = target_x_end - target_x_start#target_bars[-1].x - target_bars[0].x
        bars2_span = current_x_end - current_x_start#current_bars[-1].x - current_bars[0].x


        # Create pairs based on the smallest distances
        matches_pairs = []
        for bar1 in target_bars:
            best_match_index = SpikeLinker.get_best_bar_match(bar1, current_bars, target_x_start, current_x_start, bars1_span, bars2_span)
            best_match_bar = current_bars.pop(best_match_index)  # Remove matched bar from consideration
            matches_pairs.append((bar1, best_match_bar))

        # Perform the linking operation for each pair
        linked_bar1 = []
        linked_bar2 = []
        for bar1, bar2 in matches_pairs:
            Bar.link(bar1, bar2)
            linked_bar1.append(bar1)
            linked_bar2.append(bar2)
        return linked_bar1, linked_bar2

    def calculate_max_index(curvex, curvey, curve_range):
        max_i = -1
        max_y = 0
        cx = curvex[curve_range[0]:curve_range[1] + 1]
        cy = curvey[curve_range[0]:curve_range[1] + 1]
        for i in range(len(cy)):
            y = cy[i]
            if max_i == -1 or max_y < y:
                max_i = i
                max_y = y
        return max_i + curve_range[0]

    def calculate_centroid(split, curvex, spanx):
        start, end = split
        return ((curvex[start] + curvex[end]) / 2.0 - spanx[0]) / (spanx[1] - spanx[0])
    
    def nearest_bar(value, bars):
    # Perform a linear search to find the closest index
        closest_index = None
        closest_bar = None
        closest_distance = float('inf')
        for i, bar in enumerate(bars):
            v = bar.x
            distance = abs(v - value)
            if distance < closest_distance:
                closest_distance = distance
                closest_index = i
                closest_bar = bar
        return closest_bar
    
    def contains_overlapping_bars(bars, spanx):
        if not bars or len(bars) < 2:
            #print("->Not enough bars to check for overlap!")
            return False
        bars_x = []
        for i in range(1, len(bars)):
            bars_x.append(bars[i].x - bars[i - 1].x)
        avg_x = np.average(bars_x)
        span = spanx[1] - spanx[0]
        if span == 0:
            return False
        ratio = avg_x / span
        #print("bars", len(bars), "bars_x", len(bars_x), "avg_x", avg_x, "ratio", ratio, "threshold", OVERLAPING_BARS_THRESHOLD)
        return ratio <= OVERLAPING_BARS_THRESHOLD

    def link_splits(target_splits, target_curvex, target_curvey, target_bars, current_splits, current_curvex, current_curvey, current_bars):
        target_span = (target_curvex[target_splits[0][0]], target_curvex[target_splits[-1][1]])
        current_span = (current_curvex[current_splits[0][0]], current_curvex[current_splits[-1][1]])
        print(target_span)
        print(current_span)
    
        target_centroids = [(i, SpikeLinker.calculate_centroid(split, target_curvex, target_span)) for i, split in enumerate(target_splits)]
        current_centroids = [(i, SpikeLinker.calculate_centroid(split, current_curvex, current_span)) for i, split in enumerate(current_splits)]
        
        pairs = []
        for ti, t_centroid in target_centroids:
            for ci, c_centroid in current_centroids:
                #print("center test", ti, ":", t_centroid, "vs", ci, ":", c_centroid)
                distance = abs(t_centroid - c_centroid)
                pairs.append((distance, ti, ci))
        
        #print("pairs unsorted", pairs)
        pairs.sort()  # Sort by distance
        print("pairs sorted", pairs)
        
        target_used = set()
        current_used = set()
        matched_pairs = []
        
        for distance, ti, ci in pairs:
            if ti not in target_used and ci not in current_used:
                matched_pairs.append((target_splits[ti], current_splits[ci]))
                target_used.add(ti)
                current_used.add(ci)
        print("Found", len(matched_pairs), "pairs to link!")
        target_bars = target_bars.copy()
        current_bars = current_bars.copy()
        indexes = 10
        for matched_pair in matched_pairs:
            target_split = matched_pair[0]
            current_split = matched_pair[1]

            target_bars_in_range = SpikeLinker.get_bars_in_range(target_curvex[target_split[0]], target_curvex[target_split[1]], target_bars)
            current_bars_in_range = SpikeLinker.get_bars_in_range(current_curvex[current_split[0]], current_curvex[current_split[1]], current_bars)

            overlapping_target = SpikeLinker.contains_overlapping_bars(target_bars[target_bars_in_range[0]:target_bars_in_range[1] + 1], (target_curvex[target_split[0]], target_curvex[target_split[1]]))
            overlapping_current = SpikeLinker.contains_overlapping_bars(current_bars[current_bars_in_range[0]:current_bars_in_range[1] + 1], (current_curvex[current_split[0]], current_curvex[current_split[1]]))

            if not overlapping_target and not overlapping_current:
                #''' NO OVERLAPPING BAR X VALUES, CAN TRY THE SIMPLE MATCH APPROACH
                print("No overlapping bar x values detected, proceeding with 1-1 matching")
                max_target_index = SpikeLinker.calculate_max_index(target_curvex, target_curvey, target_split)
                max_current_index = SpikeLinker.calculate_max_index(current_curvex, current_curvey, current_split)

                #target_bar = dichotomy.nearest_index(target_curvex[max_target_index+1], [bar.x for bar in target_bars])
                #current_bar = dichotomy.nearest_index(current_curvex[max_current_index+1], [bar.x for bar in current_bars])

                target_bar_range = dichotomy.nearest_indexes(target_curvex[max_target_index+1], [bar.x for bar in target_bars], 30)
                current_bar_range = dichotomy.nearest_indexes(current_curvex[max_current_index+1], [bar.x for bar in current_bars], 30)
                
                target_bar = SpikeLinker.nearest_bar(target_curvex[max_target_index+1], target_bars[target_bar_range[0]:target_bar_range[1] + 1])
                current_bar = SpikeLinker.nearest_bar(current_curvex[max_current_index+1], current_bars[current_bar_range[0]:current_bar_range[1] + 1])
                '''
                plt.suptitle('Trinna match with this target'.format())
                plt.plot(target_curvex, target_curvey,'b-')
                plt.plot([target_bar.x],[target_curvey[max_target_index]],'v-')
                plt.show()
                plt.suptitle('Given this current curve'.format())
                plt.plot(current_curvex, current_curvey,'b-')
                plt.plot([current_bar.x],[current_curvey[max_current_index]],'v-')
                plt.show()
                '''

                
                Bar.link(target_bar, current_bar)
                target_bars.remove(target_bar) 
                current_bars.remove(current_bar)
                #'''
            else:
                #'''OVERLAPS DETECTED, PROCEEDING WITH MORE GENERAL APPROACH!
                print("Overlapping bar x values detected! Passing onto the general matching approach")
                l_target_bars, l_current_bars = SpikeLinker.link(target_curvex[target_split[0]], target_curvex[target_split[1]], target_bars, current_curvex[current_split[0]], current_curvex[current_split[1]], current_bars)
                #print("l_target_bars", l_target_bars)
                #print("l_current_bars", l_current_bars)
                for bar in l_target_bars:
                    if bar in target_bars:
                        target_bars.remove(bar)
                for bar in l_current_bars:
                    if bar in target_bars:
                        target_bars.remove(bar)

                for bar in l_target_bars:
                    if bar in current_bars:
                        current_bars.remove(bar)
                for bar in l_current_bars:
                    if bar in current_bars:
                        current_bars.remove(bar)
                if len(target_bars) == 0 or len(current_bars) == 0:
                    print("No more matches to do as there is no bars to try!")
                    break
                #'''