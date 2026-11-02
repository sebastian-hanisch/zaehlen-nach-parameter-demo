"""Orakel-Tests: Verteilungen, Momenten-Semiring und Formeln gegen unabhängige Rechenwege (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §5).

Unabhängig heißt: Aufzählen aller Schichtfolgen, Permutationen und Ordnungsbäume, Brüche statt Momenten-Semiring, die alternierende Summe für die Eulerschen Zahlen, das steigende Produkt für die
Stirling-Zahlen, die Dyck-Pfad-DP für die Narayana-Zahlen und die Potenzmethode für den Eigenwert."""

import itertools
import math
import random
from fractions import Fraction

import pytest

import zpm_algorithm as A


@pytest.mark.parametrize("letter", "FSN")
def test_shift_distribution_equals_enumeration(letter):
    for n in range(0, 13):
        assert A.shift_distribution(n, letter)[0] == A.shift_brute(n, letter)


@pytest.mark.parametrize("letter", "FSN")
def test_moments_semiring_equals_the_distribution_in_fractions(letter):
    for n in range(0, 61):
        d, _ = A.shift_distribution(n, letter)
        assert A.mean_var(d) == A.mean_var_moments(*A.shift_moments(n, letter)[0])


@pytest.mark.parametrize("letter", "FSN")
def test_moments_equal_the_enumeration(letter):
    for n in range(1, 11):
        assert A.mean_var(A.shift_brute(n, letter)) == A.mean_var_moments(*A.shift_moments(n, letter)[0])


def test_shift_totals_equal_stueck_4_and_the_transfer_matrix():
    assert sum(A.shift_distribution(3, "N")[0]) == 20 and sum(A.shift_distribution(10, "N")[0]) == 13926
    # die Gesamtzahl folgt der Rekursion der Zustände (Zahl der Folgen mit 0, 1, 2 Nächten am Ende): a0' = 2a0 + a1 + a2, a1' = a0, a2' = a1
    a0, a1, a2 = 1, 0, 0
    for n in range(1, 31):
        a0, a1, a2 = 2 * a0 + a1 + a2, a0, a1
        assert a0 + a1 + a2 == sum(A.shift_distribution(n, "N")[0])


def test_eulerian_equals_the_alternating_sum_and_the_enumeration():
    assert all(A.eulerian(n) == A.eulerian_formula(n) for n in range(1, 61))
    assert all(A.trim(A.perm_stats_brute(n)[0]) == A.eulerian(n) for n in range(1, 9))


def test_mahonian_equals_the_enumeration_and_the_naive_product():
    assert all(A.mahonian(n) == A.perm_stats_brute(n)[1] for n in range(1, 9))

    def naive(n):
        poly = [1]
        for i in range(1, n + 1):
            new = [0] * (len(poly) + i - 1)
            for k, c in enumerate(poly):
                for j in range(i):
                    new[k + j] += c
            poly = new
        return poly

    assert all(A.mahonian(n) == naive(n) for n in range(1, 31))


def test_stirling_row_equals_the_rising_product_and_the_enumeration():
    assert all(A.stirling1_row(n) == A.stirling1_polynomial(n) for n in range(0, 80))
    assert all(A.stirling1_row(n) == A.perm_stats_brute(n)[2] for n in range(1, 9))


def test_narayana_equals_the_dyck_path_dp_and_the_tree_enumeration():
    assert all(A.narayana(n) == A.dyck_peaks(n) for n in range(1, 41))
    assert all(A.narayana(n) == A.plane_trees_by_leaves(n) for n in range(1, 10))
    assert all(sum(A.narayana(n)) == math.comb(2 * n, n) // (n + 1) for n in range(1, 60))


def test_formula_mean_and_variance_equal_the_fractions():
    for n in range(2, 61):
        assert A.mean_var(A.narayana(n)) == A.formula_mean_var("Blätter", n)
        assert A.mean_var(A.eulerian(n)) == A.formula_mean_var("Abstiege", n)
        assert A.mean_var(A.mahonian(n)) == A.formula_mean_var("Inversionen", n)
        assert A.mean_var(A.stirling1_row(n)) == A.formula_mean_var("Zyklen", n)


def test_mean_variance_by_a_second_method_the_expected_value_by_enumeration():
    """Mittel und Varianz der Abstiege aus allen Permutationen von 7, Zahl für Zahl."""
    n = 7
    values = [sum(1 for i in range(n - 1) if p[i] > p[i + 1]) for p in itertools.permutations(range(n))]
    mean = Fraction(sum(values), len(values))
    var = Fraction(sum(v * v for v in values), len(values)) - mean * mean
    assert (mean, var) == A.formula_mean_var("Abstiege", n)


def test_eigenvalue_growth_equals_the_exact_increments():
    lam, mu, sigma2 = A.shift_growth("N")
    for n in (100, 200):
        m1 = A.mean_var_moments(*A.shift_moments(n, "N")[0])
        m2 = A.mean_var_moments(*A.shift_moments(n + 1, "N")[0])
        assert float(m2[0] - m1[0]) == pytest.approx(mu, abs=1e-5) and float(m2[1] - m1[1]) == pytest.approx(sigma2, abs=1e-4)


def test_tour_cost_mean_equals_the_edge_sum_over_n_minus_1():
    from zpm_scenario import random_cost, tour_cost_distribution

    rng = random.Random(3)
    for _ in range(12):
        n = rng.randint(4, 7)
        cost = random_cost(n, rng.randint(0, 999))
        d = tour_cost_distribution(n, cost)
        assert sum(d) == math.factorial(n - 1)
        assert A.mean_var(d)[0] == Fraction(sum(c for row in cost for c in row if c is not None), n - 1)
