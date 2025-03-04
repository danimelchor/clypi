def distance(this: str, other: str) -> int:
    if not this or not other:
        return max(len(this), len(other))

    n, m = len(this), len(other)
    dist = [[0 for _ in range(m + 1)] for _ in range(n + 1)]

    # Prepopulate first X and Y axis
    for t in range(0, n + 1):
        dist[t][0] = t
    for o in range(0, m + 1):
        dist[0][o] = o

    # Compute actions
    for t in range(n):
        for o in range(m):
            insertion = dist[t][o + 1] + 1
            deletion = dist[t + 1][o] + 1
            substitution = dist[t][o] + (1 if this[t] != other[o] else 0)
            dist[t + 1][o + 1] = min(insertion, deletion, substitution)

    # Get bottom right of computed matrix
    return dist[n][m]
