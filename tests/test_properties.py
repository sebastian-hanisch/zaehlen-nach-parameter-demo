"""Eigenschaften (ORACLE-PLAYBOOK §5): Aussagen, die für jede Größe gelten, auf festen Zufallsständen."""

import math
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

import zpm_algorithm as A
import zpm_evaluation as ev

ROOT = Path(__file__).resolve().parent.parent
FAMILIES = {
    "Schichtfolgen (Nächte)": lambda n: A.shift_distribution(n, "N")[0],
    "Narayana": A.narayana,
    "Eulersche Zahlen": A.eulerian,
    "Mahonische Zahlen": A.mahonian,
    "Stirling erster Art": A.stirling1_row,
}


@pytest.mark.parametrize("n", range(1, 40))
def test_totals_equal_the_known_counts(n):
    assert sum(A.eulerian(n)) == sum(A.mahonian(n)) == sum(A.stirling1_row(n)) == math.factorial(n)
    assert sum(A.narayana(n)) == math.comb(2 * n, n) // (n + 1)


@pytest.mark.parametrize("n", range(2, 40))
def test_symmetric_families_are_symmetric(n):
    assert A.is_symmetric(A.eulerian(n)) and A.is_symmetric(A.mahonian(n)) and A.is_symmetric(A.narayana(n)[1:])
    assert not A.is_symmetric(A.stirling1_row(n)[1:]) or n == 2


@pytest.mark.parametrize("name", list(FAMILIES))
def test_support_is_an_interval_and_distributions_are_log_concave(name):
    for n in range(2, 61):
        d = FAMILIES[name](n)
        ks = [k for k, c in enumerate(d) if c]
        assert all(d[k] > 0 for k in range(ks[0], ks[-1] + 1)) and A.log_concave(d), (name, n)


@pytest.mark.parametrize("name", list(FAMILIES))
def test_mean_is_inside_the_support_and_variance_is_non_negative(name):
    for n in range(1, 61):
        d = FAMILIES[name](n)
        mean, var = A.mean_var(d)
        ks = [k for k, c in enumerate(d) if c]
        assert ks[0] <= mean <= ks[-1] and var >= 0


@pytest.mark.parametrize("n", range(2, 60))
def test_mahonian_variance_is_the_sum_of_uniform_variances(n):
    """Inversionen sind eine Summe unabhängiger gleichverteilter Größen 0..i−1: die Varianz addiert sich zu Summe (i²−1)/12."""
    assert A.mean_var(A.mahonian(n))[1] == sum(Fraction(i * i - 1, 12) for i in range(1, n + 1))


@pytest.mark.parametrize("n", range(1, 70))
def test_the_three_letter_means_add_up_to_n(n):
    """Jede Folge hat n Buchstaben: die mittleren Zahlen von F, S und N ergeben zusammen n."""
    total = sum(A.mean_var_moments(*A.shift_moments(n, letter)[0])[0] for letter in "FSN")
    assert total == n


@pytest.mark.parametrize("n", range(1, 40))
def test_the_letter_distributions_sum_to_the_same_total(n):
    totals = {sum(A.shift_distribution(n, letter)[0]) for letter in "FSN"}
    assert len(totals) == 1


def test_means_grow_linearly_for_the_automaton():
    prev = None
    for n in range(80, 120):
        m = A.mean_var_moments(*A.shift_moments(n, "N")[0])
        if prev is not None:
            assert abs(float(m[0] - prev[0]) - 0.2158347366) < 1e-6 and abs(float(m[1] - prev[1]) - 0.1545692997) < 1e-6      # gleich auf sechs Stellen
        prev = m


def test_the_cycle_distribution_does_not_approach_the_normal_one():
    """Der Abstand der Zyklen bleibt über dem 10-fachen des Abstands der Abstiege (Gegenbefund)."""
    for n in (50, 200):
        assert A.kolmogorov_distance(A.stirling1_row(n)) > 10 * A.kolmogorov_distance(A.eulerian(n))
    assert A.kolmogorov_distance(A.stirling1_row(200)) > 0.02


def test_the_distance_falls_for_the_automaton_and_for_the_eulerian_numbers():
    shift = [A.kolmogorov_distance(A.shift_distribution(n, "N")[0]) for n in (10, 25, 50, 100, 200, 400)]
    assert all(x > y for x, y in zip(shift, shift[1:]))
    euler = [A.kolmogorov_distance(A.eulerian(n)) for n in (10, 50, 200)]
    assert all(x > y for x, y in zip(euler, euler[1:]))


def test_analyses_are_deterministic_across_hash_seeds():
    code = ("import sys; sys.path.insert(0, %r); import zpm_evaluation as ev; "
            "a = ev.analyse(ev.Settings('Schichtfolgen: Nächte', 30)); b = ev.analyse(ev.Settings('Permutationen: Zyklen', 12)); t = ev.tour_play(6, 5); "
            "print(a.dist, a.mean, a.var, b.dist, t['dist'], t['mean'])" % str(ROOT))
    runs = {subprocess.run([sys.executable, "-X", "utf8", "-c", code], capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONHASHSEED": str(h)}).stdout for h in (0, 1, 12345)}
    assert len(runs) == 1 and runs.pop().strip()


def test_every_statistic_gives_a_consistent_analysis():
    for stat in ("Schichtfolgen: Nächte", "Schichtfolgen: Frühschichten", "Schichtfolgen: Spätschichten", "Permutationen: Abstiege", "Permutationen: Inversionen", "Permutationen: Zyklen", "Ordnungsbäume: Blätter"):
        for n in (2, 5, 9):
            a = ev.analyse(ev.Settings(stat, n))
            assert a.problems == [] and sum(a.dist) > 0
