def nearest_index(target, data):
    max = len(data)
    if max == 0:
        return 0
    a = 0
    b = max - 1
    center = int((a + b) / 2)
    lst_center = -1

    if data[a] > target:
        return a
    if data[b] < target:
        return b

    it = 0
    while center != lst_center:
        if data[center] > target:
            b = center
        else:
            a = center
        lst_center = center
        center = int((a + b) / 2)
        it = it + 1

    return center

def nearest_cluster_index(target, clusters):
    #dycotomy time
    max = len(clusters)
    if not max:
        print("empty list of clusters...")
        return 0
    a = 0
    b = max - 1
    center = int((a + b) / 2)
    lst_center = -1
    if clusters[a].spikesX[0] > target:
        return a
        
    if clusters[b].spikesX[0] < target:
        return b

    it = 0
    while center != lst_center:
        if clusters[center].spikesX[0] > target:
            b = center
        else:
            a = center
        lst_center = center
        center = int((a + b) / 2)
        it = it + 1
        
    return center

def nearest_indexes(target, data, span_of_values):
    # Binary search for the nearest index
    low, high = 0, len(data) - 1
    best_idx = low
    while low <= high:
        mid = (low + high) // 2
        if data[mid] < target:
            low = mid + 1
        elif data[mid] > target:
            high = mid - 1
        else:
            best_idx = mid
            break
        # Update best_idx if the current mid is closer to the target
        if abs(data[mid] - target) < abs(data[best_idx] - target):
            best_idx = mid

    # Return a range around the best index
    return max(0, best_idx - span_of_values), min(len(data) - 1, best_idx + span_of_values)