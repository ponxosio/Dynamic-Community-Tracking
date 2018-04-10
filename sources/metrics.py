from typing import List


def jaccard_coefficient(g1: List[str], g2: List[str]) -> float:
    s1 = set(g1)
    s2 = set(g2)

    return len(s1.intersection(s2))/len(s1.union(s2))




