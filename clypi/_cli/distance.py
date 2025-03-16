from typing import Iterable


def distance(this: str, other: str) -> float:
    """
    Modified version of the Levenshtein distance to consider the case
    of the letters being compared so that dist(a, A) < dist(a, b)
    """
    if not this or not other:
        return max(len(this), len(other))

    n, m = len(this), len(other)
    dist: list[list[float]] = [[0 for _ in range(m + 1)] for _ in range(n + 1)]

    # Prepopulate first X and Y axis
    for t in range(0, n + 1):
        dist[t][0] = t
    for o in range(0, m + 1):
        dist[0][o] = o

    def _subst_dist(t: str, o: str) -> float:
        if t == o:
            return 0
        elif t.lower() == o.lower():
            return 0.5
        return 1

    # Compute actions
    for t in range(n):
        for o in range(m):
            insertion = dist[t][o + 1] + 1
            deletion = dist[t + 1][o] + 1
            substitution = dist[t][o] + _subst_dist(this[t], other[o])
            dist[t + 1][o + 1] = min(insertion, deletion, substitution)

    # Get bottom right of computed matrix
    return dist[n][m]


def closest(word: str, options: Iterable[str]) -> tuple[str, float]:
    """
    Given a word and a list of options, it returns the closest
    option to that word and it's distance
    """
    dists = [distance(word, o) for o in options]
    if not dists:
        return "", float("inf")
    min_opt = min(zip(options, dists), key=lambda x: x[1])
    return min_opt
