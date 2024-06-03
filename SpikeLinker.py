import numpy as np
import dichotomy

from Bar import *




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
        for bar1, bar2 in matches_pairs:
            Bar.link(bar1, bar2)
