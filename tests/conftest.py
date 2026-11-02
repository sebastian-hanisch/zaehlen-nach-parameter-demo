"""Gemeinsame Fixtures: die Mini-Instanzen, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from fractions import Fraction
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hand_shifts_3():
    """Gültige Schichtfolgen der Länge 3 (NF und NNN verboten), 20 Stück. Ohne Nacht 8; mit einer Nacht 8 (NSF, NSS, FNS, SNS, FFN, FSN, SFN, SSN); mit zwei Nächten 4 (NNS, NSN, FNN, SNN).
    Summe der Nächte 0·8 + 1·8 + 2·4 = 16, Summe k(k−1) = 2·4 = 8; Mittel 16/20 = 4/5, Varianz 8/20 + 4/5 − 16/25 = 14/25."""
    return {"dist": [8, 8, 4], "moments": (20, 16, 8), "mean": Fraction(4, 5), "var": Fraction(14, 25)}


@pytest.fixture
def hand_trees_3():
    """Ordnungsbäume mit 3 Kanten: ein Pfad (1 Blatt), drei Bäume mit 2 Blättern, ein Stern (3 Blätter): 1, 3, 1; Mittel 2, Varianz (1 + 0 + 1)/5 = 2/5."""
    return {"dist": [0, 1, 3, 1], "mean": Fraction(2), "var": Fraction(2, 5)}


@pytest.fixture
def hand_perms():
    """Permutationen von 3: Abstiege 1, 4, 1 (123: 0; 132, 213, 231, 312: 1; 321: 2); Inversionen (1+q)(1+q+q²) = 1, 2, 2, 1; Zyklen: (1)(2)(3) 3 Zyklen 1×, eine Transposition + Fixpunkt 2 Zyklen 3×, ein 3-Zyklus 1 Zyklus 2× = 0, 2, 3, 1.
    Zyklen: Mittel (2 + 6 + 3)/6 = 11/6 = H_3, Varianz 17/36. Für n = 4: 1, 11, 11, 1 / 1, 3, 5, 6, 5, 3, 1 / 0, 6, 11, 6, 1."""
    return {"des3": [1, 4, 1], "inv3": [1, 2, 2, 1], "cyc3": [0, 2, 3, 1], "cyc3_mean": Fraction(11, 6), "cyc3_var": Fraction(17, 36),
            "des4": [1, 11, 11, 1], "inv4": [1, 3, 5, 6, 5, 3, 1], "cyc4": [0, 6, 11, 6, 1]}
