"""Kennzahlen, Experimente und Verdikte. Jedes Verdikt ist eine reine Funktion (Art, Text); die App ruft st.<Art>(Text)."""

import math
import time
from dataclasses import dataclass, field
from fractions import Fraction

import zpm_algorithm as A
import zpm_constants as C
from zpm_scenario import effective_n, random_cost, split_stat, tour_cost_distribution

_SUPER = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


@dataclass(frozen=True)
class Settings:
    stat: str = C.DEFAULT_STAT
    n: int = C.DEFAULT_N
    normal: str = C.DEFAULT_NORMAL


@dataclass(frozen=True, eq=False)
class Analysis:
    settings: Settings
    family: str
    kind: str                              # Name des Parameters (Nächte, Abstiege, …)
    n_eff: int
    dist: list                             # Verteilung: dist[k] = Zahl der Strukturen mit Parameterwert k
    mean: object                           # Fraction
    var: object                            # Fraction
    ways: list                             # Rechenwege: {"Gruppe", "Weg", "Wert", "Text", "Schritte", "Grund"}
    problems: list
    notes: list
    steps: dict = field(default_factory=dict)


# ----------------------------------------------------------------------------- Formatierung

def de(x: float, digits: int = 2) -> str:
    return f"{x:.{digits}f}".replace(".", ",")


def big_text(x: int) -> str:
    """Ganze Zahl lesbar: bis 12 Stellen mit Tausenderpunkt, darüber Mantisse mal Zehnerpotenz mit Stellenzahl (ohne Stringumwandlung der ganzen Zahl)."""
    if x < 10 ** 12:
        return f"{x:,}".replace(",", ".")
    d = A.digit_count(x)
    s = str(x // 10 ** (d - 3))
    return f"{s[0]},{s[1:3]}·10{str(d - 1).translate(_SUPER)} ({d} Stellen)"


def frac_text(x: Fraction, digits: int = 4) -> str:
    """Bruch als Dezimalzahl mit Komma (exakt gerundet über ganze Zahlen)."""
    scaled = round(x * 10 ** digits)
    sign = "−" if scaled < 0 else ""
    scaled = abs(scaled)
    s = str(scaled).rjust(digits + 1, "0")
    return f"{sign}{s[:-digits]},{s[-digits:]}"


def sci_text(x: float) -> str:
    if x == 0:
        return "0"
    if 0.01 <= abs(x) < 10000:
        return de(x, 2)
    mant, exp = f"{x:.1e}".split("e")
    return f"{mant.replace('.', ',')}·10{str(int(exp)).translate(_SUPER)}"


def dist_text(d, limit: int = 14) -> str:
    """Verteilung als Liste; lange Verteilungen gekürzt (erste sechs und letzte drei Werte, dazu die Länge)."""
    d = list(d)
    if len(d) <= limit:
        return "[" + ", ".join(big_text(c) for c in d) + "]"
    return "[" + ", ".join(big_text(c) for c in d[:6]) + ", …, " + ", ".join(big_text(c) for c in d[-3:]) + f"] ({len(d)} Werte)"


# ----------------------------------------------------------------------------- Analyse der eingestellten Aufgabe

def analyse(s: Settings) -> Analysis:
    family, kind, letter = split_stat(s.stat)
    n = effective_n(s.stat, s.n)
    notes = []
    if n != s.n:
        notes.append(f"Für diese Familie rechnet die App höchstens bis n = {C.N_CAP[family]}: gerechnet wird mit n = {n}.")
    ways, problems = [], []
    steps = {}

    def add(group, name, value, text, count, reason=""):
        ways.append({"Gruppe": group, "Weg": name, "Wert": value, "Text": text, "Schritte": count, "Grund": reason})

    def skipped(group, name, reason):
        ways.append({"Gruppe": group, "Weg": name, "Wert": None, "Text": "", "Schritte": None, "Grund": reason})

    # --- Verteilung
    if family == "Schichtfolgen":
        dist, ops = A.shift_distribution(n, letter)
        steps["Verteilung"] = ops
        add("Verteilung", "Polynom je Zustand (DP)", tuple(dist), dist_text(dist), ops)
        if n <= C.ENUM_SHIFT_N:
            brute = A.shift_brute(n, letter)
            add("Verteilung", "Aufzählen aller Folgen", tuple(brute), dist_text(brute), 3 ** n)
        else:
            skipped("Verteilung", "Aufzählen aller Folgen", f"nur bis n = {C.ENUM_SHIFT_N}")
    elif family == "Ordnungsbäume":
        dist = A.narayana(n)
        add("Verteilung", "Formel C(n,k)·C(n,k−1)/n", tuple(dist), dist_text(dist), None)
        if n <= C.DYCK_N:
            dyck = A.dyck_peaks(n)
            add("Verteilung", "Dyck-Pfade nach Spitzen", tuple(dyck), dist_text(dyck), None)
        else:
            skipped("Verteilung", "Dyck-Pfade nach Spitzen", f"nur bis n = {C.DYCK_N}")
        if n <= C.ENUM_TREE_N:
            brute = A.plane_trees_by_leaves(n)
            add("Verteilung", "Aufzählen aller Ordnungsbäume", tuple(brute), dist_text(brute), math.comb(2 * n, n) // (n + 1))
        else:
            skipped("Verteilung", "Aufzählen aller Ordnungsbäume", f"nur bis n = {C.ENUM_TREE_N}")
    else:
        main, second, enum_index = {
            "Abstiege": (("Rekursion der Eulerschen Zahlen", A.eulerian), ("alternierende Summe", A.eulerian_formula), 0),
            "Inversionen": (("Produkt (1)(1+q)…(1+…+q^(n−1))", A.mahonian), None, 1),
            "Zyklen": (("Dreieck der Stirling-Zahlen", A.stirling1_row), ("steigendes Produkt x(x+1)…(x+n−1)", A.stirling1_polynomial), 2),
        }[kind]
        dist = A.trim(main[1](n))
        add("Verteilung", main[0], tuple(dist), dist_text(dist), None)
        if second is not None:
            other = A.trim(second[1](n))
            add("Verteilung", second[0], tuple(other), dist_text(other), None)
        if n <= C.ENUM_PERM_N:
            brute = A.trim(A.perm_stats_brute(n)[enum_index])
            add("Verteilung", "Aufzählen aller Permutationen", tuple(brute), dist_text(brute), math.factorial(n))
        else:
            skipped("Verteilung", "Aufzählen aller Permutationen", f"nur bis n = {C.ENUM_PERM_N}")

    # --- Mittel und Varianz
    mean, var = A.mean_var(dist)

    def mv_text(mv):
        return f"Mittel {frac_text(mv[0])}, Varianz {frac_text(mv[1])}"

    add("Mittel und Varianz", "aus der Verteilung (Brüche)", (mean, var), mv_text((mean, var)), len(dist))
    if family == "Schichtfolgen":
        (c, s1, s2), mops = A.shift_moments(n, letter)
        steps["Momente"] = mops
        mm = A.mean_var_moments(c, s1, s2)
        add("Mittel und Varianz", "Momenten-Semiring (drei Zahlen je Zustand)", mm, mv_text(mm), mops)
        if n <= C.ENUM_SHIFT_N:
            bm = A.mean_var(A.shift_brute(n, letter))
            add("Mittel und Varianz", "Aufzählen aller Folgen", bm, mv_text(bm), 3 ** n)
        else:
            skipped("Mittel und Varianz", "Aufzählen aller Folgen", f"nur bis n = {C.ENUM_SHIFT_N}")
    else:
        formula = A.formula_mean_var(kind, n)
        if formula is not None:
            add("Mittel und Varianz", "Formel", formula, mv_text(formula), None)
        else:
            skipped("Mittel und Varianz", "Formel", "für n = 1 gibt es keine Streuung zu prüfen")
    for group in sorted({w["Gruppe"] for w in ways}):
        done = [w for w in ways if w["Gruppe"] == group and w["Wert"] is not None]
        if any(w["Wert"] != done[0]["Wert"] for w in done):
            problems.append(f"{group}: " + ", ".join(w["Weg"] for w in done) + " weichen ab")
    return Analysis(s, family, kind, n, dist, mean, var, ways, problems, notes, steps)


def way_rows(a: Analysis) -> list[dict]:
    """Tabelle der Rechenwege: Frage, Weg, Ergebnis, Schritte, Prüfung."""
    rows = []
    reference = {}
    for w in a.ways:
        if w["Wert"] is not None and w["Gruppe"] not in reference:
            reference[w["Gruppe"]] = w["Wert"]
    for w in a.ways:
        if w["Wert"] is None:
            rows.append({"Frage": w["Gruppe"], "Weg": w["Weg"], "Ergebnis": "–", "Schritte": "–", "Prüfung": w["Grund"]})
        else:
            rows.append({"Frage": w["Gruppe"], "Weg": w["Weg"], "Ergebnis": w["Text"], "Schritte": "–" if w["Schritte"] is None else big_text(w["Schritte"]),
                         "Prüfung": "gleich" if w["Wert"] == reference[w["Gruppe"]] else "weicht ab"})
    return rows


def distribution_rows(a: Analysis, limit: int = 60) -> list[dict]:
    """Verteilung als Tabelle: Parameterwert, Zahl, Anteil (höchstens `limit` Zeilen um den häufigsten Wert)."""
    total = sum(a.dist)
    ks = [k for k, c in enumerate(a.dist) if c]
    if len(ks) > limit:
        mode = A.mode_of(a.dist)
        start = max(ks[0], min(mode - limit // 2, ks[-1] - limit + 1))
        ks = [k for k in ks if start <= k < start + limit]
    return [{a.kind: k, "Anzahl": big_text(a.dist[k]), "Anteil in %": de(100 * a.dist[k] / total, 3)} for k in ks]


def verdict_answers(a: Analysis):
    if a.problems:
        return "error", "Die Rechenwege widersprechen sich: " + "; ".join(a.problems)
    total = sum(a.dist)
    sd = math.sqrt(float(a.var))
    mode = A.mode_of(a.dist)
    if a.family == "Schichtfolgen":
        head = f"Gültige Schichtfolgen der Länge {a.n_eff} nach Zahl der {a.kind}"
    elif a.family == "Permutationen":
        head = f"Permutationen von {a.n_eff} Elementen nach Zahl der {a.kind}"
    else:
        head = f"Ordnungsbäume mit {a.n_eff} Kanten nach Zahl der {a.kind}"
    checked = len([w for w in a.ways if w["Wert"] is not None])
    return "success", (f"{head}: {big_text(total)} Strukturen, Mittel {frac_text(a.mean)}, Varianz {frac_text(a.var)}, Standardabweichung {de(sd, 4)}; am häufigsten {mode} mit {de(100 * a.dist[mode] / total, 2)} %. "
                       f"{checked} Rechenweg(e) geben je Frage dieselbe Zahl.")


# ----------------------------------------------------------------------------- Experiment 2: gleiche Gesamtzahl

def perm_compare() -> list[dict]:
    n = C.PERM_COMPARE_N
    rows = []
    for name, d in (("Abstiege", A.eulerian(n)), ("Inversionen", A.mahonian(n)), ("Zyklen", A.stirling1_row(n))):
        d = A.trim(d)
        mean, var = A.mean_var(d)
        rows.append({"Statistik": name, "Gesamtzahl": sum(d), "Mittel": mean, "Varianz": var, "Standardabweichung": math.sqrt(float(var)), "kleinster Wert": next(k for k, c in enumerate(d) if c),
                     "größter Wert": len(d) - 1, "dist": d})
    return rows


def verdict_perm_compare(rows: list[dict]):
    if len({r["Gesamtzahl"] for r in rows}) != 1:
        return "error", "Die Gesamtzahlen der drei Statistiken sind verschieden."
    a, i, z = rows
    return "success", (f"Alle drei zählen dieselben {big_text(a['Gesamtzahl'])} Permutationen von {C.PERM_COMPARE_N} Elementen, aber die Verteilungen sind verschieden: "
                       f"Abstiege Mittel {frac_text(a['Mittel'], 2)}, Varianz {frac_text(a['Varianz'], 2)}; Inversionen {frac_text(i['Mittel'], 2)}, {frac_text(i['Varianz'], 2)}; Zyklen {frac_text(z['Mittel'], 2)}, {frac_text(z['Varianz'], 2)}. "
                       "Die Gesamtzahl verrät nichts davon.")


# ----------------------------------------------------------------------------- Experiment 3: Mittel und Streuung wachsen

def growth_rows() -> dict:
    rows = []
    for n in C.GROWTH_NS:
        (c, s1, s2), _ = A.shift_moments(n, "N")
        (c2, t1, t2), _ = A.shift_moments(n + 1, "N")
        mean, var = A.mean_var_moments(c, s1, s2)
        mean2, var2 = A.mean_var_moments(c2, t1, t2)
        rows.append({"n": n, "Mittel": mean, "Varianz": var, "Zuwachs Mittel": mean2 - mean, "Zuwachs Varianz": var2 - var})
    lam, mu, sigma2 = A.shift_growth("N")
    return {"rows": rows, "lambda": lam, "mu": mu, "sigma2": sigma2}


def verdict_growth(res: dict):
    last = res["rows"][-1]
    inc_m, inc_v = float(last["Zuwachs Mittel"]), float(last["Zuwachs Varianz"])
    if abs(inc_m - res["mu"]) > 1e-4 or abs(inc_v - res["sigma2"]) > 1e-4:
        return "error", f"Zuwachs ({inc_m:.5f}, {inc_v:.5f}) und Eigenwertrechnung ({res['mu']:.5f}, {res['sigma2']:.5f}) weichen ab."
    return "success", (f"Beim Schichtautomaten wachsen Mittel und Varianz der Nächte linear: je Schritt um {de(inc_m, 5)} und {de(inc_v, 5)} (n = {last['n']}), "
                       f"gleich den Ableitungen des größten Eigenwerts λ = {de(res['lambda'], 6)} aus Stück 2: μ = {de(res['mu'], 5)}, σ² = {de(res['sigma2'], 5)}.")


# ----------------------------------------------------------------------------- Experiment 4: wie normal

def normality_rows() -> list[dict]:
    rows = []
    for n in C.NORMAL_SHIFT_NS:
        rows.append({"Familie": "Nachtschichten", "n": n, "Abstand": A.kolmogorov_distance(A.shift_distribution(n, "N")[0])})
    for name, f in (("Eulersche Zahlen (Abstiege)", A.eulerian), ("Narayana (Blätter)", A.narayana), ("Stirling erster Art (Zyklen)", A.stirling1_row)):
        for n in C.NORMAL_OTHER_NS:
            rows.append({"Familie": name, "n": n, "Abstand": A.kolmogorov_distance(f(n))})
    return rows


def verdict_normality(rows: list[dict]):
    def pick(name, n):
        return next(r["Abstand"] for r in rows if r["Familie"] == name and r["n"] == n)

    s_lo, s_hi = pick("Nachtschichten", C.NORMAL_SHIFT_NS[0]), pick("Nachtschichten", C.NORMAL_SHIFT_NS[-1])
    st_lo, st_hi = pick("Stirling erster Art (Zyklen)", C.NORMAL_OTHER_NS[0]), pick("Stirling erster Art (Zyklen)", C.NORMAL_OTHER_NS[-1])
    kind = "warning" if st_hi > 0.5 * st_lo else "success"
    return kind, (f"Der Abstand zur Normalverteilung fällt bei den Nachtschichten von {de(s_lo, 4)} (n = {C.NORMAL_SHIFT_NS[0]}) auf {de(s_hi, 4)} (n = {C.NORMAL_SHIFT_NS[-1]}), "
                  f"bei den Zyklen der Permutationen bleibt er bei {de(st_lo, 4)} (n = {C.NORMAL_OTHER_NS[0]}) und {de(st_hi, 4)} (n = {C.NORMAL_OTHER_NS[-1]}): "
                  "dort wächst die Varianz nur logarithmisch, die Normalverteilung ist hier eine deutlich schlechtere Näherung als bei den anderen Familien. Gleiche Streuung heißt nicht gleiche Form.")


# ----------------------------------------------------------------------------- Experiment 5: Aufwand

def effort_rows() -> list[dict]:
    rows = []
    for n in C.EFFORT_NS:
        dist, dops = A.shift_distribution(n, "N")
        (c, s1, s2), mops = A.shift_moments(n, "N")
        same = A.mean_var(dist) == A.mean_var_moments(c, s1, s2)
        rows.append({"n": n, "Werte der Verteilung": len(dist), "Stellen der Gesamtzahl": A.digit_count(sum(dist)), "Additionen Verteilung": dops, "Additionen Momente": mops,
                     "Faktor": dops / mops, "gleiches Mittel und gleiche Varianz": same})
    return rows


def verdict_effort(rows: list[dict]):
    if not all(r["gleiches Mittel und gleiche Varianz"] for r in rows):
        return "error", "Verteilung und Momenten-Semiring liefern verschiedene Mittel oder Varianzen."
    last = rows[-1]
    return "success", (f"Für n = {last['n']} hat die Verteilung {last['Werte der Verteilung']} Werte; sie braucht {big_text(last['Additionen Verteilung'])} Additionen, "
                       f"das Momenten-Semiring {big_text(last['Additionen Momente'])} (nach der Zählregel der Demo etwa {de(last['Faktor'], 0)}-mal weniger; die Laufzeit unterscheidet sich weniger) und liefert dasselbe Mittel und dieselbe Varianz. "
                       "Wer nur Mittel und Streuung braucht, muss die Verteilung nicht speichern.")


def time_experiment() -> list[dict]:
    rows = []
    for n in C.TIME_NS:
        t0 = time.perf_counter()
        A.shift_distribution(n, "N")
        t1 = time.perf_counter()
        A.shift_moments(n, "N")
        t2 = time.perf_counter()
        rows.append({"n": n, "Verteilung (Sekunden)": t1 - t0, "Momente (Sekunden)": t2 - t1})
    return rows


def verdict_time(rows: list[dict]):
    last = rows[-1]
    return "info", (f"Gemessen auf diesem Rechner (Python): n = {last['n']}: Verteilung {de(last['Verteilung (Sekunden)'], 3)} s, Momente {de(last['Momente (Sekunden)'], 4)} s "
                    f"(etwa das {de(last['Verteilung (Sekunden)'] / max(last['Momente (Sekunden)'], 1e-9), 0)}-fache). Eine Messung, keine Garantie.")


# ----------------------------------------------------------------------------- Spielwiese: Kostenverteilung einer Rundreise

def tour_play(n: int, seed: int) -> dict:
    n = max(C.PLAY_N_MIN, min(n, C.PLAY_N_MAX))
    cost = random_cost(n, seed)
    dist = tour_cost_distribution(n, cost)
    mean, var = A.mean_var(dist)
    edges = sum(c for row in cost for c in row if c is not None)
    return {"n": n, "seed": seed, "dist": dist, "mean": mean, "var": var, "edges": edges, "expected": Fraction(edges, n - 1), "cycles": sum(dist)}


def verdict_tour(res: dict):
    if res["mean"] != res["expected"]:
        return "error", f"Das Mittel ({res['mean']}) ist nicht Summe/(n−1) ({res['expected']})."
    return "success", (f"{big_text(res['cycles'])} Rundreisen mit Kosten von {next(k for k, c in enumerate(res['dist']) if c)} bis {len(res['dist']) - 1}; Mittel {frac_text(res['mean'], 3)} = Summe aller Kantenkosten "
                       f"{res['edges']} geteilt durch n − 1 = {res['n'] - 1} (jede Kante liegt in gleich vielen Rundreisen), Varianz {frac_text(res['var'], 3)}.")
