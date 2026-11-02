"""Szenario: aus den Einstellungen Familie, Parameter und die wirklich gerechnete Größe bestimmen; zufällige Kostenmatrix für die Spielwiese."""

import itertools
import random

import zpm_constants as C


def split_stat(stat: str):
    """(Familie, Parameter, Buchstabe) zu einer Statistik aus der Auswahl."""
    if stat not in C.STAT_INFO:
        raise ValueError(f"unbekannte Statistik {stat!r}")
    return C.STAT_INFO[stat]


def effective_n(stat: str, n: int) -> int:
    """Die Größe, mit der die App wirklich rechnet (je Familie begrenzt)."""
    family = split_stat(stat)[0]
    return max(C.N_MIN, min(n, C.N_CAP[family], C.N_MAX))


def random_cost(n: int, seed: int, r: int = C.PLAY_R) -> list:
    """Kostenmatrix des vollständigen Digraphen: jede Kante kostet 1 bis r (deterministisch aus dem Seed)."""
    rng = random.Random(seed)
    return [[None if i == j else rng.randint(1, r) for j in range(n)] for i in range(n)]


def tour_cost_distribution(n: int, cost: list) -> list:
    """Zahl der Hamiltonkreise ab Stadt 0 je Gesamtkosten durch Aufzählen aller (n−1)! Reihenfolgen."""
    dist = {}
    for perm in itertools.permutations(range(1, n)):
        path = (0,) + perm
        total = sum(cost[a][b] for a, b in zip(path, path[1:] + (0,)))
        dist[total] = dist.get(total, 0) + 1
    return [dist.get(k, 0) for k in range(max(dist) + 1)]
