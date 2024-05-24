


def _try_generator_for_chunk(target_chunk, current_chunks, current_index_offset):
    current_chunks = current_chunks[current_index_offset:]
    if not current_chunks:
        return []
    
    target_span = target_chunk.spikesX[-1] - target_chunk.spikesX[0]
    current_end_index = 0
    best_current_end_index = -1
    best_current_span = -1
    best_current_dist = -1
    while target_span > best_current_span and current_end_index < len(current_chunks):
        current_span = current_chunks[current_end_index].spikes[-1] - current_chunks[current_end_index].spikes[0]
        current_dist = abs(current_span - target_span)
        if best_current_end_index == -1 or current_dist < best_current_dist:
            best_current_end_index = current_end_index
            best_current_span = current_span
            best_current_dist = current_dist
        #if we did find a best match, and current dist to target is growing, we won't find better anymore
        if best_current_dist != -1 and best_current_dist < current_dist:
            break
        current_end_index += 1
    return current_chunks[0:best_current_end_index]

# target chunks can be anything, but current chunks HAS to be CONTIGUOUS
def generate(target_chunks, current_chunks):
    candidates = {}
    for chunk in target_chunks:
        current_chunks_candidates = _try_generator_for_chunk(chunk, current_chunks)
        candidates[chunk] = current_chunks_candidates
    return candidates