"""Jede Zahl aus der README und aus den Texten der App, nachgerechnet (DEMO-PLAYBOOK §4). Es gibt keine Zeit als Zahl; die Zahlen sind exakt oder Bänder."""

import math
from fractions import Fraction

import zpm_algorithm as A
import zpm_constants as C
import zpm_evaluation as ev

S = ev.Settings


def test_readme_hand_instances():
    assert A.shift_distribution(3, "N")[0] == [8, 8, 4] and sum([8, 8, 4]) == 20 and A.shift_moments(3, "N")[0] == (20, 16, 8)
    assert A.narayana(3)[1:] == [1, 3, 1] and A.eulerian(4) == [1, 11, 11, 1] and A.mahonian(3) == [1, 2, 2, 1] and A.stirling1_row(4)[1:] == [6, 11, 6, 1]
    assert A.shift_distribution(3, "F")[0] == [7, 8, 4, 1] and A.shift_distribution(3, "S")[0] == [3, 10, 6, 1]


def test_readme_standard_case():
    d, _ = A.shift_distribution(10, "N")
    assert d == [1024, 2816, 4096, 3472, 1852, 571, 91, 4] and sum(d) == 13926
    mean, var = A.mean_var(d)
    assert (round(float(mean), 4), round(float(var), 4)) == (2.3166, 1.6581) and A.mode_of(d) == 2 and round(100 * d[2] / sum(d), 2) == 29.41
    assert round(math.sqrt(float(var)), 4) == 1.2877


def test_readme_known_distributions_against_their_formulas():
    for n in range(2, 61):
        assert A.mean_var(A.narayana(n)) == (Fraction(n + 1, 2), Fraction(n * n - 1, 4 * (2 * n - 1)))
        assert A.mean_var(A.eulerian(n)) == (Fraction(n - 1, 2), Fraction(n + 1, 12))
        assert A.mean_var(A.mahonian(n)) == (Fraction(n * (n - 1), 4), Fraction(n * (n - 1) * (2 * n + 5), 72))
        assert A.mean_var(A.stirling1_row(n)) == (A.harmonic(n), A.harmonic(n) - A.harmonic(n, 2))


def test_readme_same_total_different_distribution():
    rows = ev.perm_compare()
    assert [(r["Statistik"], str(r["Mittel"]), str(r["Varianz"])) for r in rows] == [("Abstiege", "9/2", "11/12"), ("Inversionen", "45/2", "125/4"), ("Zyklen", "7381/2520", "350339/254016")]
    assert [round(float(r["Mittel"]), 4) for r in rows] == [4.5, 22.5, 2.929] and [round(float(r["Varianz"]), 4) for r in rows] == [0.9167, 31.25, 1.3792]
    assert all(sum(r["dist"]) == 3628800 for r in rows) and [(r["kleinster Wert"], r["größter Wert"]) for r in rows] == [(0, 9), (0, 45), (1, 10)]


def test_readme_growth_for_the_automaton():
    res = ev.growth_rows()
    assert [(r["n"], round(float(r["Mittel"]), 2), round(float(r["Varianz"]), 2)) for r in res["rows"]] == [(50, 10.95, 7.84), (100, 21.74, 15.57), (200, 43.33, 31.03), (400, 86.49, 61.94), (800, 172.83, 123.77)]
    assert all(round(float(r["Zuwachs Mittel"]), 6) == 0.215835 and round(float(r["Zuwachs Varianz"]), 6) == 0.154569 for r in res["rows"])
    assert (round(res["lambda"], 6), round(res["mu"], 5), round(res["sigma2"], 5)) == (2.546818, 0.21583, 0.15457)


def test_readme_distance_to_the_normal_distribution():
    pick = {(r["Familie"], r["n"]): r["Abstand"] for r in ev.normality_rows()}
    assert [round(pick[("Nachtschichten", n)], 5) for n in C.NORMAL_SHIFT_NS] == [0.01324, 0.00946, 0.00671, 0.00467, 0.00324, 0.0023]
    assert [round(pick[("Nachtschichten", n)] * math.sqrt(n), 3) for n in C.NORMAL_SHIFT_NS] == [0.042, 0.047, 0.047, 0.047, 0.046, 0.046]
    assert [round(pick[("Eulersche Zahlen (Abstiege)", n)], 5) for n in C.NORMAL_OTHER_NS] == [0.00923, 0.0019, 0.00049]
    assert [round(pick[("Narayana (Blätter)", n)], 5) for n in C.NORMAL_OTHER_NS] == [0.00554, 0.00124, 0.00031]
    assert [round(pick[("Stirling erster Art (Zyklen)", n)], 5) for n in C.NORMAL_OTHER_NS] == [0.02544, 0.02858, 0.02533]


def test_readme_log_concavity():
    assert all(A.log_concave(A.shift_distribution(n, "N")[0]) for n in range(1, 201))
    assert all(A.log_concave(A.narayana(n)[1:]) and A.log_concave(A.eulerian(n)) for n in range(2, 201))
    assert all(A.log_concave(A.stirling1_row(n)[1:]) for n in range(2, 101)) and all(A.log_concave(A.mahonian(n)) for n in range(2, 61))


def test_readme_effort():
    rows = ev.effort_rows()
    assert [(r["n"], r["Werte der Verteilung"], r["Stellen der Gesamtzahl"], r["Additionen Verteilung"], r["Additionen Momente"]) for r in rows] == [
        (100, 68, 41, 30295, 2980), (400, 268, 163, 481195, 11980), (1000, 668, 407, 3002995, 29980)]
    assert [round(r["Faktor"], 1) for r in rows] == [10.2, 40.2, 100.2]


def test_readme_tour_cost_distribution():
    res = ev.tour_play(7, 35)
    assert (res["cycles"], res["edges"], res["mean"], res["var"]) == (720, 114, Fraction(19), Fraction(43, 3))
    assert (next(k for k, c in enumerate(res["dist"]) if c), len(res["dist"]) - 1) == (10, 33)
    assert round(float(res["var"]), 3) == 14.333 and ev.tour_play(8, 35)["cycles"] == 5040


def test_readme_presets():
    s = ev.Settings
    a = ev.analyse(s(**C.PRESETS["Standardfall: Nachtschichten, n = 10"]))
    assert a.dist[0] == 1024 and a.dist[7] == 4 and round(float(a.mean), 2) == 2.32 and round(float(a.var), 2) == 1.66
    trees = ev.analyse(s(**C.PRESETS["Blätter von Ordnungsbäumen, n = 12"]))
    assert trees.mean == Fraction(13, 2) and sum(trees.dist) == 208012
    des, inv, cyc = (ev.analyse(s(**C.PRESETS[f"{n} in Permutationen, n = 12"])) for n in ("Abstiege", "Inversionen", "Zyklen"))
    assert (des.mean, des.var) == (Fraction(11, 2), Fraction(13, 12)) and inv.mean == 33 and A.is_symmetric(des.dist) and round(float(cyc.mean), 2) == 3.10
    assert sum(ev.analyse(s(**C.PRESETS["Frühschichten, n = 20"])).dist) == sum(A.shift_distribution(20, "N")[0])
    assert A.digit_count(sum(ev.analyse(s(**C.PRESETS["Lange Folgen: Spätschichten, n = 400"])).dist)) == 163


def test_app_text_limits_come_from_the_constants():
    assert (C.N_MAX, C.N_CAP, C.ENUM_SHIFT_N, C.ENUM_PERM_N, C.ENUM_TREE_N, C.DYCK_N) == (400, {"Schichtfolgen": 400, "Permutationen": 150, "Ordnungsbäume": 200}, 12, 8, 9, 60)
    assert (C.PERM_COMPARE_N, C.GROWTH_NS, C.NORMAL_SHIFT_NS, C.NORMAL_OTHER_NS, C.EFFORT_NS, C.TIME_NS) == (10, (50, 100, 200, 400, 800), (10, 25, 50, 100, 200, 400), (10, 50, 200), (100, 400, 1000), (400, 1000))
    assert (C.PLAY_N_MIN, C.PLAY_N_MAX, C.PLAY_R, C.PLAY_SEED_DEFAULT) == (4, 8, 5, 35)
