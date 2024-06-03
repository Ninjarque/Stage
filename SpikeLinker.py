import numpy as np
import dichotomy

from Bar import *




class SpikeLinker:
    def __init__(self):
        pass

    def get_bar_dist(bar1, bar2, bars1_x_offset, bars2_x_offset):
        if not bar1 or not bar2:
            return 100000
        return ((bar1.x - bars1_x_offset) - (bar2.x - bars2_x_offset)) * ((bar1.x - bars1_x_offset) - (bar2.x - bars2_x_offset))
    
    def get_best_bar_match(bar1, bars2, bars1_x_offset, bars2_x_offset):
        best_index = -1
        best_dist = 10000

        b2i = 0
        for bar2 in bars2:
            dist = SpikeLinker.get_bar_dist(bar1, bar2, bars1_x_offset, bars2_x_offset)

            if dist < best_dist or best_index == -1:
                best_index = b2i
                best_dist = dist

            b2i += 1

        return best_index
        

    def link(target_x_start, target_x_end, target_bars, current_x_start, current_x_end, current_bars):
        target_start = dichotomy.nearest_index(target_x_start, [bar.x for bar in target_bars])
        target_end = dichotomy.nearest_index(target_x_end, [bar.x for bar in target_bars]) + 1
        target_bars = target_bars[target_start:target_end]
        
        current_start = dichotomy.nearest_index(current_x_start, [bar.x for bar in current_bars])
        current_end = dichotomy.nearest_index(current_x_end, [bar.x for bar in current_bars]) + 1
        current_bars = current_bars[current_start:current_end]

        # Determine which list is shorter and use it as the target list
        if len(target_bars) > len(current_bars):
            target_bars, current_bars = current_bars, target_bars
            target_x_start, current_x_start = current_x_start, target_x_start
            target_x_end, current_x_end = current_x_end, target_x_end

        
        print("len target bars", len(target_bars), "len current bars", len(current_bars))


        # Create pairs based on the smallest distances
        matches_pairs = []
        for bar1 in target_bars:
            best_match_index = SpikeLinker.get_best_bar_match(bar1, current_bars, target_x_start, current_x_start)
            best_match_bar = current_bars.pop(best_match_index)  # Remove matched bar from consideration
            matches_pairs.append((bar1, best_match_bar))

        # Perform the linking operation for each pair
        for bar1, bar2 in matches_pairs:
            Bar.link(bar1, bar2)
