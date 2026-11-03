"""Einheitentests des Rechenkerns an von Hand gerechneten Werten (DEMO-PLAYBOOK §1b)."""

import math
from fractions import Fraction

import pytest

import zpm_algorithm as A


def test_shift_distribution_and_moments_by_hand(hand_shifts_3):
    assert A.shift_distribution(3, "N")[0] == hand_shifts_3["dist"] == A.shift_brute(3, "N")
    assert A.shift_moments(3, "N")[0] == hand_shifts_3["moments"]
    assert A.mean_var(hand_shifts_3["dist"]) == (hand_shifts_3["mean"], hand_shifts_3["var"])
    assert A.mean_var_moments(*hand_shifts_3["moments"]) == (hand_shifts_3["mean"], hand_shifts_3["var"])


def test_shift_other_letters_by_hand():
    # Von Hand aus den 20 Folgen der Länge 3: Frühschichten 7, 8, 4, 1 (null: 1 + 3 + 3 aus den Gruppen ohne, mit einer, mit zwei Nächten), Spätschichten 3, 10, 6, 1
    assert A.shift_distribution(3, "F")[0] == [7, 8, 4, 1] == A.shift_brute(3, "F")
    assert A.shift_distribution(3, "S")[0] == [3, 10, 6, 1] == A.shift_brute(3, "S")


def test_shift_step_counts_by_hand():
    # Momenten-Semiring: fünf Additionen je Übergang (a + c; b + s1 + w·c; d + s2 + 2·w·s1); Übergänge je Schritt 3, 5, dann 6 (Zustände 0, 1, 2 mit 3, 2, 1 Kanten)
    assert [A.shift_moments(n, "N")[1] for n in (1, 2, 3, 4)] == [15, 40, 70, 100]
    assert A.shift_distribution(0, "N") == ([1], 0) and A.shift_moments(0, "N") == ((1, 0, 0), 0)


def test_narayana_by_hand(hand_trees_3):
    assert A.narayana(3) == hand_trees_3["dist"] and A.mean_var(hand_trees_3["dist"]) == (hand_trees_3["mean"], hand_trees_3["var"])
    assert A.narayana(4) == [0, 1, 6, 6, 1] and A.dyck_peaks(4) == [0, 1, 6, 6, 1] and A.plane_trees_by_leaves(3) == [0, 1, 3, 1]
    assert A.narayana(0) == [1] and A.dyck_peaks(0) == [1]


def test_permutation_distributions_by_hand(hand_perms):
    assert A.eulerian(3) == A.eulerian_formula(3) == hand_perms["des3"] and A.eulerian(4) == A.eulerian_formula(4) == hand_perms["des4"]
    assert A.mahonian(3) == hand_perms["inv3"] and A.mahonian(4) == hand_perms["inv4"]
    assert A.stirling1_row(3) == A.stirling1_polynomial(3) == hand_perms["cyc3"] and A.stirling1_row(4) == A.stirling1_polynomial(4) == hand_perms["cyc4"]
    assert A.mean_var(hand_perms["cyc3"]) == (hand_perms["cyc3_mean"], hand_perms["cyc3_var"]) == (A.harmonic(3), A.harmonic(3) - A.harmonic(3, 2))
    assert A.perm_stats_brute(3) == (hand_perms["des3"], hand_perms["inv3"], hand_perms["cyc3"])


def test_formula_values_by_hand():
    assert A.formula_mean_var("Blätter", 3) == (Fraction(2), Fraction(2, 5)) and A.formula_mean_var("Abstiege", 4) == (Fraction(3, 2), Fraction(5, 12))
    assert A.formula_mean_var("Inversionen", 3) == (Fraction(3, 2), Fraction(3 * 2 * 11, 72)) and A.formula_mean_var("Zyklen", 3) == (Fraction(11, 6), Fraction(17, 36))
    assert A.formula_mean_var("Abstiege", 1) is None and A.formula_mean_var("Nächte", 5) is None


def test_mode_trim_symmetry_log_concavity():
    assert A.mode_of([1, 5, 5, 2]) == 1 and A.mode_of([0, 0, 3]) == 2 and A.trim([1, 2, 0, 0]) == [1, 2] and A.trim([0]) == [0]
    assert A.is_symmetric([1, 11, 11, 1]) and not A.is_symmetric([1, 2, 3])
    assert A.log_concave([1, 3, 3, 1]) and not A.log_concave([1, 0, 1])


def test_kolmogorov_distance_by_hand():
    # Zwei gleich häufige Werte 0 und 1: Mittel 1/2, Standardabweichung 1/2. Bei k = 0: |1/2 − Φ(0)| = 0; bei k = 1: |1 − Φ(2)| = 1 − Φ(2) ≈ 0,02275
    assert A.normal_cdf(0) == 0.5 and A.normal_cdf(2) == pytest.approx(0.9772498680518208)
    assert A.kolmogorov_distance([1, 1]) == pytest.approx(1 - 0.9772498680518208, abs=1e-12)
    assert A.kolmogorov_distance([5]) == 1.0                                         # keine Streuung
    assert 0.0 < A.kolmogorov_distance([1, 3, 3, 1]) < 0.1


def test_shift_growth_by_hand():
    lam, mu, sigma2 = A.shift_growth("N")
    assert lam == pytest.approx(2.546818, abs=1e-6) and mu == pytest.approx(0.215835, abs=1e-5) and sigma2 == pytest.approx(0.154569, abs=1e-4)
    assert A.shift_eigenvalue("N", 1.0) == pytest.approx(lam)
    # Gesamtzahlen wachsen mit der Wachstumsrate aus Stück 2: λ ≈ Verhältnis aufeinanderfolgender Gesamtzahlen
    t = [sum(A.shift_distribution(n, "N")[0]) for n in (60, 61)]
    assert t[1] / t[0] == pytest.approx(lam, rel=1e-9)


def test_digit_count():
    assert A.digit_count(0) == 1 and A.digit_count(999) == 3 and A.digit_count(1000) == 4 and A.digit_count(10 ** 5000) == 5001
    with pytest.raises(ValueError):
        A.digit_count(-1)


def test_invalid_input_is_refused():
    with pytest.raises(ValueError):
        A.shift_distribution(3, "X")
    with pytest.raises(ValueError):
        A.shift_moments(-1, "N")
    with pytest.raises(ValueError):
        A.mean_var([0, 0])
