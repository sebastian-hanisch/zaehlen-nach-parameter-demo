"""Randfälle: kleinste Größen, Grenzen der Regler, jede Statistik, große Zahlen (die 4300-Stellen-Grenze von `str`), Formatierung."""

from fractions import Fraction

import pytest

import zpm_algorithm as A
import zpm_constants as C
import zpm_evaluation as ev
import zpm_scenario as S


def test_size_zero_has_one_structure_with_parameter_zero():
    assert A.shift_distribution(0, "N") == ([1], 0) and A.eulerian(0) == [1] and A.mahonian(0) == [1] and A.stirling1_row(0) == [1] and A.narayana(0) == [1]


def test_size_one_distributions():
    assert A.shift_distribution(1, "N")[0] == [2, 1] and A.shift_distribution(1, "F")[0] == [2, 1] and A.shift_distribution(1, "S")[0] == [2, 1]
    assert A.eulerian(1) == [1] and A.mahonian(1) == [1] and A.stirling1_row(1) == [0, 1] and A.narayana(1) == [0, 1]


def test_size_two_distributions():
    assert A.eulerian(2) == [1, 1] and A.mahonian(2) == [1, 1] and A.stirling1_row(2) == [0, 1, 1] and A.narayana(2) == [0, 1, 1]
    assert A.shift_distribution(2, "N")[0] == A.shift_brute(2, "N") == [4, 3, 1]       # nach dem Ausschluss von NF


def test_variance_of_a_single_valued_distribution_is_zero():
    assert A.mean_var([0, 0, 7]) == (Fraction(2), Fraction(0)) and A.kolmogorov_distance([7]) == 1.0
    assert ev.analyse(ev.Settings("Permutationen: Abstiege", 1)).var == 0 and ev.analyse(ev.Settings("Permutationen: Abstiege", 1)).dist == [1]


def test_formula_is_skipped_for_size_one_and_marked():
    a = ev.analyse(ev.Settings("Permutationen: Abstiege", 1))
    row = next(r for r in ev.way_rows(a) if r["Weg"] == "Formel")
    assert row["Ergebnis"] == "–" and "keine Streuung" in row["Prüfung"] and a.problems == []


def test_effective_n_caps_per_family():
    assert S.effective_n("Schichtfolgen: Nächte", 400) == 400 and S.effective_n("Permutationen: Zyklen", 400) == 150 and S.effective_n("Ordnungsbäume: Blätter", 400) == 200
    assert S.effective_n("Ordnungsbäume: Blätter", 0) == 1
    with pytest.raises(ValueError):
        S.effective_n("Unsinn", 5)
    with pytest.raises(ValueError):
        S.split_stat("Unsinn")


def test_a_capped_size_gives_a_note():
    a = ev.analyse(ev.Settings("Permutationen: Inversionen", 400))
    assert a.n_eff == 150 and a.notes and "höchstens bis n = 150" in a.notes[0]
    assert not ev.analyse(ev.Settings("Schichtfolgen: Nächte", 400)).notes


def test_huge_numbers_are_formatted_without_str_limits():
    assert ev.big_text(10 ** 5000).endswith("(5001 Stellen)") and ev.big_text(0) == "0" and ev.big_text(12345) == "12.345"
    big = ev.analyse(ev.Settings("Permutationen: Inversionen", 150))
    assert A.digit_count(sum(big.dist)) == 263 and big.problems == []


def test_largest_inputs_run_and_agree():
    a = ev.analyse(ev.Settings("Schichtfolgen: Nächte", 400))
    assert a.problems == [] and len(a.dist) == 268 and a.steps["Momente"] == 5 * (3 + 5 + 6 * 398)
    b = ev.analyse(ev.Settings("Ordnungsbäume: Blätter", 200))
    assert b.problems == [] and len(b.dist) == 201 and b.mean == Fraction(201, 2)


def test_frac_and_sci_text():
    assert ev.frac_text(Fraction(7381, 2520), 4) == "2,9290" and ev.frac_text(Fraction(1, 3), 2) == "0,33" and ev.frac_text(Fraction(-4, 3), 1) == "−1,3" and ev.frac_text(Fraction(0), 2) == "0,00"
    assert ev.sci_text(0) == "0" and ev.sci_text(0.5) == "0,50" and ev.sci_text(1.5e-10) == "1,5·10⁻¹⁰" and ev.sci_text(27646.99) == "2,8·10⁴" and ev.de(3.14159, 3) == "3,142"


def test_distribution_rows_windows_long_distributions_around_the_mode():
    a = ev.analyse(ev.Settings("Permutationen: Inversionen", 100))
    rows = ev.distribution_rows(a, 30)
    ks = [r["Inversionen"] for r in rows]
    assert len(rows) == 30 and ks == list(range(ks[0], ks[0] + 30)) and ks[0] <= A.mode_of(a.dist) < ks[-1] + 1
    small = ev.analyse(ev.Settings("Ordnungsbäume: Blätter", 3))
    assert [r["Blätter"] for r in ev.distribution_rows(small)] == [1, 2, 3] and ev.distribution_rows(small)[1]["Anteil in %"] == "60,000"


def test_tour_play_clamps_its_input_and_is_deterministic():
    res = ev.tour_play(99, 5)
    assert res["n"] == C.PLAY_N_MAX and res["cycles"] == 5040 and ev.tour_play(1, 5)["n"] == C.PLAY_N_MIN
    assert ev.tour_play(5, 7)["dist"] == ev.tour_play(5, 7)["dist"] and ev.tour_play(5, 7)["dist"] != ev.tour_play(5, 8)["dist"]


@pytest.mark.parametrize("stat", C.STATS)
@pytest.mark.parametrize("n", [1, 2, 3])
def test_every_statistic_works_at_the_smallest_sizes(stat, n):
    a = ev.analyse(ev.Settings(stat, n))
    assert a.problems == [] and ev.verdict_answers(a)[0] == "success" and ev.way_rows(a) and ev.distribution_rows(a)
