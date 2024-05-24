CANDIDATE_THRESHOLD_RATIO = 2.0
CANDIDATE_MEAN_OR_MAX_RATIO = 0.6 #0.0

def _try_generator_for_chunk(target_chunk, current_chunks, current_index_offset):
    current_chunks = current_chunks[current_index_offset:]
    if not current_chunks:
        return []
    if current_chunks[0].is_over_noise_threshold(threshold_ratio=CANDIDATE_THRESHOLD_RATIO, mean_or_max_ratio=CANDIDATE_MEAN_OR_MAX_RATIO):
        return [current_chunks[0]]
    else:
        return []
    target_span = target_chunk.spikesX[-1] - target_chunk.spikesX[0]
    current_end_index = 0
    best_current_end_index = -1
    best_current_span = -1
    best_current_dist = -1

    full_noise = True
    while target_span > best_current_span and current_end_index < len(current_chunks):
        if current_chunks[current_end_index].is_over_noise_threshold(threshold_ratio=CANDIDATE_THRESHOLD_RATIO, mean_or_max_ratio=CANDIDATE_MEAN_OR_MAX_RATIO):
            full_noise = False
        current_span = current_chunks[current_end_index].spikesX[-1] - current_chunks[current_end_index].spikesX[0]
        current_dist = abs(current_span - target_span)
        if best_current_end_index == -1 or current_dist < best_current_dist:
            best_current_end_index = current_end_index
            best_current_span = current_span
            best_current_dist = current_dist
        #if we did find a best match, and current dist to target is growing, we won't find better anymore
        if best_current_dist != -1 and best_current_dist < current_dist:
            break
        current_end_index += 1
    if full_noise:
        print("discarding full noise option!")
        return []
    
    best_current_end_index += 1
    res = current_chunks[0:best_current_end_index]
    #print("len current chunks:", len(current_chunks))
    #print("hey", 0, ":", best_current_end_index, "->", res)
    return res

# target chunks can be anything, but current chunks HAS to be CONTIGUOUS
def generate(target_chunks, current_chunks):
    candidates = {}
    for chunk in target_chunks:
        for current_index_offset in range(len(current_chunks)):
            current_chunks_candidates = _try_generator_for_chunk(chunk, current_chunks, current_index_offset)
            if not chunk in candidates:
                candidates[chunk] = []
            if current_chunks_candidates:
                candidates[chunk].append(current_chunks_candidates)
    return candidates