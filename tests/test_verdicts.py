"""Verdikte und Formatierung an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import math
from fractions import Fraction

import zpm_algorithm as A
import zpm_constants as C
import zpm_evaluation as ev

S = ev.Settings


def test_formatting():
    assert ev.de(3.14159, 3) == "3,142" and ev.big_text(0) == "0" and ev.big_text(1234567) == "1.234.567" and ev.big_text(10 ** 12) == "1,00·10¹² (13 Stellen)"
    assert ev.dist_text([1, 2, 3]) == "[1, 2, 3]" and ev.dist_text(list(range(20))) == "[0, 1, 2, 3, 4, 5, …, 17, 18, 19] (20 Werte)" and ev.dist_text([1024, 2816]) == "[1.024, 2.816]"


def test_verdict_answers_for_the_standard_case(hand_shifts_3):
    a = ev.analyse(S())
    assert ev.verdict_answers(a) == ("success", "Gültige Schichtfolgen der Länge 10 nach Zahl der Nächte: 13.926 Strukturen, Mittel 2,3166, Varianz 1,6581, Standardabweichung 1,2877; am häufigsten 2 mit 29,41 %. "
                                                "5 Rechenweg(e) geben je Frage dieselbe Zahl.")
    small = ev.analyse(S("Schichtfolgen: Nächte", 3))
    assert small.dist == hand_shifts_3["dist"] and small.mean == hand_shifts_3["mean"] and small.var == hand_shifts_3["var"]
    assert "20 Strukturen, Mittel 0,8000, Varianz 0,5600" in ev.verdict_answers(small)[1]


def test_verdict_answers_for_the_other_families():
    assert ev.verdict_answers(ev.analyse(S("Ordnungsbäume: Blätter", 12))) == ("success", "Ordnungsbäume mit 12 Kanten nach Zahl der Blätter: 208.012 Strukturen, Mittel 6,5000, Varianz 1,5543, Standardabweichung 1,2467; "
                                                                                       "am häufigsten 6 mit 29,32 %. 4 Rechenweg(e) geben je Frage dieselbe Zahl.")
    assert ev.verdict_answers(ev.analyse(S("Permutationen: Abstiege", 12)))[1].startswith("Permutationen von 12 Elementen nach Zahl der Abstiege: 479.001.600 Strukturen, Mittel 5,5000, Varianz 1,0833")
    assert ev.verdict_answers(ev.analyse(S("Permutationen: Zyklen", 12)))[1].startswith("Permutationen von 12 Elementen nach Zahl der Zyklen: 479.001.600 Strukturen, Mittel 3,1032, Varianz 1,5382")
    assert "Mittel 33,0000, Varianz 53,1667" in ev.verdict_answers(ev.analyse(S("Permutationen: Inversionen", 12)))[1]
    assert ev.verdict_answers(ev.analyse(S("Schichtfolgen: Spätschichten", 400)))[1].startswith("Gültige Schichtfolgen der Länge 400 nach Zahl der Spätschichten: 3,04·10¹⁶² (163 Stellen) Strukturen, Mittel 190,3253")


def test_verdict_answers_reports_a_disagreement_as_an_error():
    a = ev.analyse(S())
    broken = ev.Analysis(a.settings, a.family, a.kind, a.n_eff, a.dist, a.mean, a.var, a.ways, ["Verteilung: x, y weichen ab"], [], a.steps)
    assert ev.verdict_answers(broken) == ("error", "Die Rechenwege widersprechen sich: Verteilung: x, y weichen ab")


def test_analyse_reports_a_wrong_way_as_a_problem(monkeypatch):
    real = A.shift_moments
    monkeypatch.setattr(A, "shift_moments", lambda n, letter="N": ((20, 17, 8), 1) if n == 3 else real(n, letter))
    a = ev.analyse(S("Schichtfolgen: Nächte", 3))
    assert a.problems and "Mittel und Varianz" in a.problems[0] and ev.verdict_answers(a)[0] == "error"


def test_way_rows_for_a_small_case():
    rows = ev.way_rows(ev.analyse(S("Schichtfolgen: Nächte", 3)))
    assert rows[0] == {"Frage": "Verteilung", "Weg": "Polynom je Zustand (DP)", "Ergebnis": "[8, 8, 4]", "Schritte": "31", "Prüfung": "gleich"}
    assert rows[1] == {"Frage": "Verteilung", "Weg": "Aufzählen aller Folgen", "Ergebnis": "[8, 8, 4]", "Schritte": "27", "Prüfung": "gleich"}
    assert rows[3]["Weg"] == "Momenten-Semiring (drei Zahlen je Zustand)" and rows[3]["Schritte"] == "42" and rows[3]["Ergebnis"] == "Mittel 0,8000, Varianz 0,5600"
    big = ev.way_rows(ev.analyse(S("Permutationen: Abstiege", 12)))
    assert big[2]["Prüfung"] == "nur bis n = 8" and big[0]["Schritte"] == "–"


def test_way_rows_flag_a_deviating_way():
    a = ev.analyse(S("Permutationen: Zyklen", 6))
    ways = [dict(w) for w in a.ways]
    ways[1]["Wert"], ways[1]["Text"] = (0, 1), "[0, 1]"
    rows = ev.way_rows(ev.Analysis(a.settings, a.family, a.kind, a.n_eff, a.dist, a.mean, a.var, ways, [], [], a.steps))
    assert rows[0]["Prüfung"] == "gleich" and rows[1]["Prüfung"] == "weicht ab"


def test_distribution_rows():
    a = ev.analyse(S("Schichtfolgen: Nächte", 3))
    assert ev.distribution_rows(a) == [{"Nächte": 0, "Anzahl": "8", "Anteil in %": "40,000"}, {"Nächte": 1, "Anzahl": "8", "Anteil in %": "40,000"}, {"Nächte": 2, "Anzahl": "4", "Anteil in %": "20,000"}]


def test_perm_compare_and_verdict():
    rows = ev.perm_compare()
    assert [(r["Statistik"], r["Mittel"], r["Varianz"], r["kleinster Wert"], r["größter Wert"]) for r in rows] == [
        ("Abstiege", Fraction(9, 2), Fraction(11, 12), 0, 9), ("Inversionen", Fraction(45, 2), Fraction(125, 4), 0, 45), ("Zyklen", Fraction(7381, 2520), Fraction(350339, 254016), 1, 10)]
    assert all(r["Gesamtzahl"] == math.factorial(10) for r in rows)
    assert ev.verdict_perm_compare(rows) == ("success", "Alle drei zählen dieselben 3.628.800 Permutationen von 10 Elementen, aber die Verteilungen sind verschieden: "
                                                         "Abstiege Mittel 4,50, Varianz 0,92; Inversionen 22,50, 31,25; Zyklen 2,93, 1,38. Die Gesamtzahl verrät nichts davon.")
    assert ev.verdict_perm_compare([dict(rows[0], Gesamtzahl=5)] + rows[1:])[0] == "error"


def test_growth_rows_and_verdict():
    res = ev.growth_rows()
    assert [r["n"] for r in res["rows"]] == list(C.GROWTH_NS)
    assert all(abs(float(r["Zuwachs Mittel"]) - 0.2158347) < 1e-6 and abs(float(r["Zuwachs Varianz"]) - 0.1545693) < 1e-6 for r in res["rows"])
    assert round(res["lambda"], 6) == 2.546818 and round(res["mu"], 5) == 0.21583 and round(res["sigma2"], 5) == 0.15457
    assert ev.verdict_growth(res) == ("success", "Beim Schichtautomaten wachsen Mittel und Varianz der Nächte linear: je Schritt um 0,21583 und 0,15457 (n = 800), "
                                                 "gleich den Ableitungen des größten Eigenwerts λ = 2,546818 aus Stück 2: μ = 0,21583, σ² = 0,15457.")
    assert ev.verdict_growth(dict(res, mu=0.3))[0] == "error"


def test_normality_rows_and_verdict():
    rows = ev.normality_rows()
    pick = {(r["Familie"], r["n"]): r["Abstand"] for r in rows}
    assert [round(pick[("Nachtschichten", n)], 5) for n in C.NORMAL_SHIFT_NS] == [0.01324, 0.00946, 0.00671, 0.00467, 0.00324, 0.0023]
    assert [round(pick[("Eulersche Zahlen (Abstiege)", n)], 5) for n in C.NORMAL_OTHER_NS] == [0.00923, 0.0019, 0.00049]
    assert [round(pick[("Narayana (Blätter)", n)], 5) for n in C.NORMAL_OTHER_NS] == [0.00554, 0.00124, 0.00031]
    assert [round(pick[("Stirling erster Art (Zyklen)", n)], 5) for n in C.NORMAL_OTHER_NS] == [0.02544, 0.02858, 0.02533]
    kind, text = ev.verdict_normality(rows)
    assert kind == "warning" and "von 0,0132 (n = 10) auf 0,0023 (n = 400)" in text and "bei 0,0254 (n = 10) und 0,0253 (n = 200)" in text
    falling = [dict(r, Abstand=r["Abstand"] / (1 + r["n"])) if r["Familie"].startswith("Stirling") else r for r in rows]
    assert ev.verdict_normality(falling)[0] == "success"


def test_effort_rows_and_verdict():
    rows = ev.effort_rows()
    assert [(r["n"], r["Werte der Verteilung"], r["Stellen der Gesamtzahl"], r["Additionen Verteilung"], r["Additionen Momente"]) for r in rows] == [
        (100, 68, 41, 30295, 1788), (400, 268, 163, 481195, 7188), (1000, 668, 407, 3002995, 17988)]
    assert [r["Additionen Momente"] for r in rows] == [3 * (3 + 5 + 6 * (n - 2)) for n in C.EFFORT_NS] and all(r["gleiches Mittel und gleiche Varianz"] for r in rows)
    assert ev.verdict_effort(rows) == ("success", "Für n = 1000 hat die Verteilung 668 Werte; sie braucht 3.002.995 Additionen, das Momenten-Semiring 17.988 (etwa 167-mal weniger) und liefert dasselbe Mittel und dieselbe Varianz. "
                                                  "Wer nur Mittel und Streuung braucht, muss die Verteilung nicht speichern.")
    assert ev.verdict_effort([dict(rows[0], **{"gleiches Mittel und gleiche Varianz": False})])[0] == "error"


def test_time_experiment_shape_and_verdict_text():
    rows = [{"n": 400, "Verteilung (Sekunden)": 0.09, "Momente (Sekunden)": 0.002}, {"n": 1000, "Verteilung (Sekunden)": 0.96, "Momente (Sekunden)": 0.0075}]
    assert ev.verdict_time(rows) == ("info", "Gemessen auf diesem Rechner (Python): n = 1000: Verteilung 0,960 s, Momente 0,0075 s (etwa das 128-fache). Eine Messung, keine Garantie.")
    res = ev.time_experiment()
    assert [r["n"] for r in res] == list(C.TIME_NS) and all(r["Verteilung (Sekunden)"] >= 0 and r["Momente (Sekunden)"] >= 0 for r in res)


def test_tour_play_and_verdict():
    res = ev.tour_play(7, 35)
    assert (res["n"], res["cycles"], res["edges"], res["mean"], res["var"]) == (7, 720, 114, Fraction(19), Fraction(43, 3)) and res["expected"] == Fraction(114, 6)
    assert ev.verdict_tour(res) == ("success", "720 Rundreisen mit Kosten von 10 bis 33; Mittel 19,000 = Summe aller Kantenkosten 114 geteilt durch n − 1 = 6 (jede Kante liegt in gleich vielen Rundreisen), Varianz 14,333.")
    assert ev.verdict_tour(dict(res, mean=Fraction(20)))[0] == "error" and ev.tour_play(8, 35)["cycles"] == 5040
