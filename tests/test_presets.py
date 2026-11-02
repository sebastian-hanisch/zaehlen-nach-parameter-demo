"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, jedes Preset zeigt etwas anderes."""

import zpm_constants as C
import zpm_evaluation as ev
import zpm_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_regler_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["stat"] in C.STATS and C.N_MIN <= preset["n"] <= C.N_MAX and preset["normal"] in C.NORMAL_CHOICES, name


def test_preset_sizes_are_inside_the_family_caps():
    for name, preset in C.PRESETS.items():
        assert preset["n"] <= C.N_CAP[C.STAT_INFO[preset["stat"]][0]], name


def test_every_preset_passes_the_checker_without_notes():
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        assert a.problems == [] and a.notes == [] and a.n_eff == preset["n"], name


def test_first_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[next(iter(C.PRESETS))]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_presets_show_what_their_help_says():
    stats = {name: ev.analyse(ev.Settings(**p)) for name, p in C.PRESETS.items()}
    assert stats["Blätter von Ordnungsbäumen, n = 12"].family == "Ordnungsbäume" and stats["Zyklen in Permutationen, n = 12"].settings.normal == "nein"
    assert stats["Lange Folgen: Spätschichten, n = 400"].kind == "Spätschichten" and stats["Frühschichten, n = 20"].kind == "Frühschichten"
    assert len({(a.settings.stat, a.n_eff) for a in stats.values()}) == len(C.PRESETS)
