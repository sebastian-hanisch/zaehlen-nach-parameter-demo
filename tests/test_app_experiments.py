"""AppTest-Durchläufe der Experimente, des Permalinks und der Spielwiese (die allgemeinen Rauchtests stehen in test_app.py)."""

import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import zpm_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _app(query: dict | None = None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (query or {}).items():
        at.query_params[key] = value
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _all_text(at) -> str:
    return " | ".join(e.value for e in list(at.success) + list(at.info) + list(at.warning) + list(at.error))


def _metrics(at) -> dict:
    return {m.label: m.value for m in at.metric}


def test_standard_case_shows_the_known_values_and_no_error():
    at = _app()
    assert not at.error
    assert _metrics(at) == {"Gesamtzahl der Strukturen": "13.926", "Mittel": "2,3166", "Standardabweichung": "1,2877", "Häufigster Wert (Nächte)": "2"}
    assert any(e.value.startswith("Gültige Schichtfolgen der Länge 10 nach Zahl der Nächte: 13.926 Strukturen, Mittel 2,3166, Varianz 1,6581") for e in at.success)
    assert any(e.value == "Alle gerechneten Wege geben je Frage dieselbe Zahl." for e in at.success)


def test_experiments_two_to_five_show_their_verdicts_without_a_click():
    text = _all_text(_app())
    assert "Alle drei zählen dieselben 3.628.800 Permutationen von 10 Elementen" in text and "Zyklen 2,93, 1,38" in text
    assert "je Schritt um 0,21583 und 0,15457 (n = 800)" in text and "λ = 2,546818" in text
    assert "bei den Zyklen der Permutationen bleibt er bei 0,0254 (n = 10) und 0,0253 (n = 200)" in text
    assert "das Momenten-Semiring 17.988 (etwa 167-mal weniger)" in text
    assert "720 Rundreisen mit Kosten von 10 bis 33; Mittel 19,000" in text


def test_time_measurement_runs_on_click():
    at = _app()
    at.button(key="time_run").click().run(timeout=TIMEOUT)
    assert not at.exception and any("Gemessen auf diesem Rechner (Python)" in i.value for i in at.info)


@pytest.mark.parametrize("name,total,mean", [("Blätter von Ordnungsbäumen, n = 12", "208.012", "6,5000"), ("Abstiege in Permutationen, n = 12", "479.001.600", "5,5000"),
                                             ("Inversionen in Permutationen, n = 12", "479.001.600", "33,0000"), ("Zyklen in Permutationen, n = 12", "479.001.600", "3,1032")])
def test_presets_show_their_numbers(name, total, mean):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error
    assert _metrics(at)["Gesamtzahl der Strukturen"] == total and _metrics(at)["Mittel"] == mean


def test_long_sequences_show_a_huge_total():
    at = _app()
    at.sidebar.button(key="preset_Lange Folgen: Spätschichten, n = 400").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error and "163 Stellen" in _metrics(at)["Gesamtzahl der Strukturen"] and _metrics(at)["Häufigster Wert (Spätschichten)"] == "190"


def test_size_is_capped_with_a_note():
    at = _app({"stat": "Permutationen: Zyklen", "n": "400"})
    assert not at.exception and any("höchstens bis n = 150" in i.value for i in at.info)
    assert _metrics(at)["Gesamtzahl der Strukturen"].endswith("Stellen)")


def test_permalink_loads_and_clamps_the_values():
    at = _app({"stat": "Ordnungsbäume: Blätter", "n": "99999", "normal": "nein"})
    assert at.sidebar.selectbox(key="stat_select").value == "Ordnungsbäume: Blätter" and at.sidebar.slider(key="n_slider").value == C.N_MAX and at.sidebar.selectbox(key="normal_select").value == "nein"


def test_permalink_with_garbage_is_ignored():
    at = _app({"stat": "kein Name", "n": "abc", "normal": "vielleicht"})
    assert at.sidebar.selectbox(key="stat_select").value == C.DEFAULT_STAT and at.sidebar.slider(key="n_slider").value == C.DEFAULT_N and at.sidebar.selectbox(key="normal_select").value == C.DEFAULT_NORMAL


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_renders_without_error_or_checker_message(name):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run(timeout=TIMEOUT)
    assert not at.exception and not at.error, name


def test_every_statistic_renders_without_error_at_small_and_medium_sizes():
    for stat in C.STATS:
        for n in ("1", "7", "30"):
            at = _app({"stat": stat, "n": n})
            assert not at.error, (stat, n, [e.value for e in at.error])


def test_playground_changes_with_its_widgets():
    at = _app()
    at.slider(key="play_n").set_value(5).run(timeout=TIMEOUT)
    assert not at.exception and any(e.value.startswith("24 Rundreisen mit Kosten von") for e in at.success)
    at.number_input(key="play_seed").set_value(7).run(timeout=TIMEOUT)
    assert not at.exception and not at.error


def test_pdf_can_be_made_for_the_extreme_settings():
    for query in ({"n": "1"}, {"stat": "Schichtfolgen: Nächte", "n": "400"}, {"stat": "Permutationen: Inversionen", "n": "150"}, {"stat": "Ordnungsbäume: Blätter", "n": "200"}, {"stat": "Permutationen: Zyklen", "n": "2"}):
        at = _app(query)
        at.button(key="pdf_make").click().run(timeout=TIMEOUT)
        assert not at.exception, query
