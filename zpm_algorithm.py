"""Rechenkern: Zählen nach Parameter. Verteilungen (Schichtfolgen nach Buchstaben, Narayana-, Eulersche, Mahonische und Stirling-Zahlen), Momenten-Semiring, Mittel und Varianz in Brüchen,
Abstand zur Normalverteilung, Eigenwert des Schichtautomaten, Aufzählen.

Eine Verteilung ist eine Liste `d`: d[k] = Zahl der Strukturen mit Parameterwert k (ganze Zahlen). Mittel und Varianz sind `Fraction`; Gleitkommazahlen kommen nur im Abstand zur
Normalverteilung und im Eigenwert vor."""

import itertools
import math
from fractions import Fraction
from functools import lru_cache

C = math.comb


# ----------------------------------------------------------------------------- Zahlen

def digit_count(x: int) -> int:
    """Zahl der Dezimalstellen einer ganzen Zahl x >= 0, ohne sie in einen String zu wandeln (Python begrenzt die Umwandlung auf 4300 Stellen)."""
    if x < 0:
        raise ValueError("x darf nicht negativ sein")
    d = max(1, int(x.bit_length() * 0.30102999566398))
    while 10 ** d <= x:
        d += 1
    while d > 1 and 10 ** (d - 1) > x:
        d -= 1
    return d


def mean_var(d) -> tuple:
    """Mittel und Varianz einer Verteilung als Brüche."""
    total = sum(d)
    if total == 0:
        raise ValueError("leere Verteilung")
    mean = Fraction(sum(k * c for k, c in enumerate(d)), total)
    return mean, Fraction(sum(k * k * c for k, c in enumerate(d)), total) - mean * mean


def mean_var_moments(c: int, s1: int, s2: int) -> tuple:
    """Mittel und Varianz aus (Zahl, Summe der Parameter, Summe von k(k−1))."""
    mean = Fraction(s1, c)
    return mean, Fraction(s2, c) + mean - mean * mean


def mode_of(d) -> int:
    """Häufigster Parameterwert (der kleinste, wenn es mehrere gibt)."""
    return max(range(len(d)), key=lambda k: (d[k], -k))


def trim(d) -> list:
    d = list(d)
    while len(d) > 1 and d[-1] == 0:
        d.pop()
    return d


# ----------------------------------------------------------------------------- Schichtautomat (Stück 1)

LETTERS = "FSN"
# Zustand = Zahl der Nächte am Ende (0, 1, 2); nach einer Nacht ist keine Frühschicht erlaubt, nach zwei Nächten keine dritte.
_NEXT = {0: (("F", 0), ("S", 0), ("N", 1)), 1: (("S", 0), ("N", 2)), 2: (("S", 0),)}


def _check_letter(letter):
    if letter not in LETTERS:
        raise ValueError(f"Buchstabe {letter!r} ist keine Schicht (F, S oder N)")


def shift_distribution(n: int, letter: str = "N"):
    """Zahl der gültigen Folgen der Länge n nach Zahl der Buchstaben `letter`. Gibt (Verteilung, Zahl der Additionen)."""
    _check_letter(letter)
    if n < 0:
        raise ValueError("n darf nicht negativ sein")
    dp = {0: [1]}
    ops = 0
    for _ in range(n):
        new = {}
        for st, poly in dp.items():
            for ch, nxt in _NEXT[st]:
                w = 1 if ch == letter else 0
                t = new.setdefault(nxt, [0] * (len(poly) + 1))
                for k, c in enumerate(poly):
                    t[k + w] += c
                    ops += 1
        dp = new
    total = [0] * (n + 1)
    for poly in dp.values():
        for k, c in enumerate(poly):
            total[k] += c
    return trim(total), ops


def shift_moments(n: int, letter: str = "N"):
    """(Zahl der Folgen, Summe der Parameter, Summe von k(k−1)) über das Momenten-Semiring: je Zustand drei Zahlen (Ableitungen der Reihe bei y = 1). Gibt (Tripel, Zahl der Additionen: fünf je Übergang, wie im Code ausgeführt; die abschließende Summation über die Zustände zählt nicht mit)."""
    _check_letter(letter)
    if n < 0:
        raise ValueError("n darf nicht negativ sein")
    dp = {0: (1, 0, 0)}
    ops = 0
    for _ in range(n):
        new = {}
        for st, (c, s1, s2) in dp.items():
            for ch, nxt in _NEXT[st]:
                w = 1 if ch == letter else 0
                a, b, d = new.get(nxt, (0, 0, 0))
                new[nxt] = (a + c, b + s1 + w * c, d + s2 + 2 * w * s1)
                ops += 5  # a + c; b + s1 + w·c; d + s2 + 2·w·s1: 1 + 2 + 2 Additionen je Übergang (auch bei w = 0 ausgeführt)
        dp = new
    return tuple(sum(v[i] for v in dp.values()) for i in range(3)), ops


def shift_brute(n: int, letter: str = "N") -> list:
    _check_letter(letter)
    dist = {}
    for seq in itertools.product(LETTERS, repeat=n):
        s = "".join(seq)
        if "NF" in s or "NNN" in s:
            continue
        dist[s.count(letter)] = dist.get(s.count(letter), 0) + 1
    return [dist.get(k, 0) for k in range(max(dist) + 1)]


def shift_eigenvalue(letter: str, y: float) -> float:
    """Größter Eigenwert der Übergangsmatrix mit Gewicht y je Buchstabe `letter` (Potenzverfahren, Gleitkomma)."""
    _check_letter(letter)
    m = [[0.0] * 3 for _ in range(3)]
    for st, moves in _NEXT.items():
        for ch, nxt in moves:
            m[st][nxt] += y if ch == letter else 1.0
    v = [1.0, 1.0, 1.0]
    lam = 1.0
    for _ in range(4000):
        w = [sum(v[i] * m[i][j] for i in range(3)) for j in range(3)]
        lam = max(w)
        v = [x / lam for x in w]
    return lam


def shift_growth(letter: str = "N", h: float = 1e-3) -> tuple:
    """(größter Eigenwert bei y = 1, Mittel je Schritt μ = d ln λ / d ln y, Varianz je Schritt σ² = d² ln λ(eᵗ)/dt²) aus dem Eigenwert."""
    lam = shift_eigenvalue(letter, 1.0)
    up, down = math.log(shift_eigenvalue(letter, math.exp(h))), math.log(shift_eigenvalue(letter, math.exp(-h)))
    return lam, (up - down) / (2 * h), (up - 2 * math.log(lam) + down) / h ** 2


# ----------------------------------------------------------------------------- bekannte Verteilungen

def narayana(n: int) -> list:
    """Ordnungsbäume mit n Kanten nach Zahl der Blätter: N(n, k) = C(n,k)·C(n,k−1)/n, k = 1..n; Index = Blätter (d[0] = 0)."""
    if n < 1:
        return [1]
    return [0] + [C(n, k) * C(n, k - 1) // n for k in range(1, n + 1)]


def dyck_peaks(n: int) -> list:
    """Dyck-Pfade mit n Aufwärtsschritten nach Zahl der Spitzen (ein Aufwärts- direkt gefolgt von einem Abwärtsschritt), durch eine Pfad-DP; Spitzen = Blätter der Ordnungsbäume."""
    if n < 1:
        return [1]

    def add(target, key, poly, shift):
        t = target.setdefault(key, [])
        if len(t) < len(poly) + shift:
            t.extend([0] * (len(poly) + shift - len(t)))
        for k, c in enumerate(poly):
            t[k + shift] += c

    state = {(0, False): [1]}                                 # (Höhe, letzter Schritt war aufwärts) -> Verteilung der Spitzen
    for step in range(2 * n):
        new = {}
        for (h, up), poly in state.items():
            if (step + h) // 2 < n:                           # bisherige Aufwärtsschritte = (Schritte + Höhe) / 2
                add(new, (h + 1, True), poly, 0)
            if h > 0:
                add(new, (h - 1, False), poly, 1 if up else 0)
        state = new
    return trim(state[(0, False)])


def plane_trees_by_leaves(n: int) -> list:
    """Ordnungsbäume mit n Kanten nach Zahl der Blätter durch Aufzählen aller Bäume."""
    @lru_cache(maxsize=None)
    def forests(total):
        if total == 0:
            return [()]
        out = []
        for s in range(1, total + 1):
            for tree in forests(s - 1):
                for rest in forests(total - s):
                    out.append((tree,) + rest)
        return out

    def leaves(t):
        return 1 if not t else sum(leaves(c) for c in t)

    dist = {}
    for t in forests(n):
        k = leaves(t)
        dist[k] = dist.get(k, 0) + 1
    return [dist.get(k, 0) for k in range(max(dist) + 1)]


def eulerian(n: int) -> list:
    """Permutationen nach Abstiegen (Eulersche Zahlen): A(n, k) = (k+1)·A(n−1, k) + (n−k)·A(n−1, k−1), k = 0..n−1."""
    if n < 1:
        return [1]
    a = [1]
    for m in range(2, n + 1):
        a = [(k + 1) * (a[k] if k < len(a) else 0) + (m - k) * (a[k - 1] if k >= 1 else 0) for k in range(m)]
    return a


def eulerian_formula(n: int) -> list:
    """Dieselben Zahlen über die alternierende Summe A(n, k) = Σ_j (−1)^j · C(n+1, j) · (k + 1 − j)^n."""
    if n < 1:
        return [1]
    return [sum((-1) ** j * C(n + 1, j) * (k + 1 - j) ** n for j in range(k + 2)) for k in range(n)]


def mahonian(n: int) -> list:
    """Permutationen nach Inversionen (Mahonische Zahlen): Koeffizienten von (1)(1+q)(1+q+q²)…(1+…+q^(n−1)), je Faktor über gleitende Summen."""
    poly = [1]
    for i in range(2, n + 1):
        length = len(poly) + i - 1
        prefix = [0]
        for c in poly:
            prefix.append(prefix[-1] + c)
        poly = [prefix[min(k + 1, len(poly))] - prefix[max(0, k - i + 1)] for k in range(length)]
    return poly


def stirling1_row(n: int) -> list:
    """Permutationen nach Zyklen (Stirling-Zahlen erster Art): c(n, k) = (n−1)·c(n−1, k) + c(n−1, k−1); Index = Zyklen (d[0] = 0 für n >= 1)."""
    row = [1]
    for m in range(1, n + 1):
        new = [0] * (m + 1)
        for k, c in enumerate(row):
            new[k] += (m - 1) * c
            new[k + 1] += c
        row = new
    return row


def stirling1_polynomial(n: int) -> list:
    """Dieselben Zahlen als Koeffizienten des steigenden Produkts x(x+1)(x+2)…(x+n−1)."""
    poly = [1]
    for i in range(n):
        new = [0] * (len(poly) + 1)
        for k, c in enumerate(poly):
            new[k] += i * c
            new[k + 1] += c
        poly = new
    return poly


def perm_stats_brute(n: int) -> tuple:
    """(Abstiege, Inversionen, Zyklen) aller Permutationen als Verteilungen durch Aufzählen."""
    des, inv, cyc = {}, {}, {}
    for p in itertools.permutations(range(n)):
        d = sum(1 for i in range(n - 1) if p[i] > p[i + 1])
        v = sum(1 for i in range(n) for j in range(i + 1, n) if p[i] > p[j])
        seen, c = set(), 0
        for s in range(n):
            if s not in seen:
                c += 1
                x = s
                while x not in seen:
                    seen.add(x)
                    x = p[x]
        des[d] = des.get(d, 0) + 1
        inv[v] = inv.get(v, 0) + 1
        cyc[c] = cyc.get(c, 0) + 1
    return [des.get(k, 0) for k in range(max(des) + 1)], [inv.get(k, 0) for k in range(max(inv) + 1)], [cyc.get(k, 0) for k in range(max(cyc) + 1)]


def harmonic(n: int, p: int = 1) -> Fraction:
    return sum(Fraction(1, j ** p) for j in range(1, n + 1))


def formula_mean_var(kind: str, n: int):
    """Mittel und Varianz aus der bekannten Formel (aus dem Gedächtnis, im Test gegen Brüche und Aufzählen bestätigt), None wenn es keine gibt oder n zu klein ist."""
    if kind == "Blätter" and n >= 2:
        return Fraction(n + 1, 2), Fraction(n * n - 1, 4 * (2 * n - 1))
    if kind == "Abstiege" and n >= 2:
        return Fraction(n - 1, 2), Fraction(n + 1, 12)
    if kind == "Inversionen" and n >= 2:
        return Fraction(n * (n - 1), 4), Fraction(n * (n - 1) * (2 * n + 5), 72)
    if kind == "Zyklen" and n >= 1:
        return harmonic(n), harmonic(n) - harmonic(n, 2)
    return None


# ----------------------------------------------------------------------------- Normalnäherung

def normal_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def kolmogorov_distance(d) -> float:
    """Größter Abstand zwischen der Verteilungsfunktion und der Normalverteilung mit gleichem Mittel und gleicher Varianz (Stetigkeitskorrektur k + 1/2)."""
    total = sum(d)
    mean, var = mean_var(d)
    mu, sd = float(mean), math.sqrt(float(var))
    if sd == 0:
        return 1.0
    cum, worst = 0, 0.0
    for k, c in enumerate(d):
        cum += c
        worst = max(worst, abs(cum / total - normal_cdf((k + 0.5 - mu) / sd)))
    return worst


def log_concave(d) -> bool:
    """Newton-Ungleichung c_k² >= c_(k−1)·c_(k+1) für alle inneren k."""
    return all(d[k] * d[k] >= d[k - 1] * d[k + 1] for k in range(1, len(d) - 1))


def is_symmetric(d) -> bool:
    return list(d) == list(reversed(d))
