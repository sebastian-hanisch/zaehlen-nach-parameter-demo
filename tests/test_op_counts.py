"""Zählung gegen Rechnung: Die gemeldete Zahl der Additionen muss die Zahl der im Code tatsächlich ausgeführten Additionen sein.

Unabhängige Zählung: Der Quelltext der Funktion wird mit Zahlen einer Klasse ausgeführt, die jede Addition mitzählt
(die Funktion selbst zählt nichts davon mit). Gezählt wird die Übergangsschleife; die abschließende Summation über die Zustände
(eine Addition je Wert) gehört nicht zur Zählregel und wird abgezogen.
"""
import inspect
import textwrap

import pytest

import zpm_algorithm as A


class Counted(int):
    adds = 0

    def __add__(self, other):
        Counted.adds += 1
        return Counted(int(self) + int(other))

    __radd__ = __add__

    def __mul__(self, other):
        return Counted(int(self) * int(other))

    __rmul__ = __mul__


def _instrumented(func, replacements):
    src = textwrap.dedent(inspect.getsource(func))
    for old, new in replacements:
        assert old in src, old
        src = src.replace(old, new)
    ns = dict(vars(A), Counted=Counted)
    exec(src, ns)
    return ns[func.__name__]


def _final_states(n):
    states = {0}
    for _ in range(n):
        states = {nxt for st in states for _, nxt in A._NEXT[st]}
    return len(states)


@pytest.mark.parametrize("letter", ["F", "S", "N"])
@pytest.mark.parametrize("n", [1, 2, 3, 5, 12, 40])
def test_moments_counter_equals_executed_additions(n, letter):
    f = _instrumented(A.shift_moments, [("dp = {0: (1, 0, 0)}", "dp = {0: (Counted(1), Counted(0), Counted(0))}")])
    Counted.adds = 0
    triple, _ = f(n, letter)
    executed = Counted.adds - 3 * _final_states(n)  # Summation am Ende abziehen
    assert tuple(int(v) for v in triple) == A.shift_moments(n, letter)[0]
    assert A.shift_moments(n, letter)[1] == executed


@pytest.mark.parametrize("letter", ["F", "S", "N"])
@pytest.mark.parametrize("n", [1, 2, 3, 5, 12, 40])
def test_distribution_counter_equals_executed_additions(n, letter):
    f = _instrumented(A.shift_distribution, [("dp = {0: [1]}", "dp = {0: [Counted(1)]}"), ("[0] * (len(poly) + 1)", "[Counted(0)] * (len(poly) + 1)")])
    Counted.adds = 0
    dist, _ = f(n, letter)
    # Summation am Ende: eine Addition je Koeffizient je Zustand; die Zahl der Koeffizienten je Zustand läuft mit dem Polynomgrad (Länge = Schritt + 1)
    final = _final_states(n) * (n + 1)
    executed = Counted.adds - final
    assert [int(v) for v in dist] == A.shift_distribution(n, letter)[0]
    assert A.shift_distribution(n, letter)[1] == executed
