"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

# Statistik -> (Familie, Name des Parameters, Buchstabe beim Schichtautomaten)
STAT_INFO = {
    "Schichtfolgen: Nächte": ("Schichtfolgen", "Nächte", "N"),
    "Schichtfolgen: Frühschichten": ("Schichtfolgen", "Frühschichten", "F"),
    "Schichtfolgen: Spätschichten": ("Schichtfolgen", "Spätschichten", "S"),
    "Permutationen: Abstiege": ("Permutationen", "Abstiege", None),
    "Permutationen: Inversionen": ("Permutationen", "Inversionen", None),
    "Permutationen: Zyklen": ("Permutationen", "Zyklen", None),
    "Ordnungsbäume: Blätter": ("Ordnungsbäume", "Blätter", None),
}
STATS = tuple(STAT_INFO)
DEFAULT_STAT = "Schichtfolgen: Nächte"
NORMAL_CHOICES = ("ja", "nein")
DEFAULT_NORMAL = "ja"
N_MIN, N_MAX, DEFAULT_N = 1, 400, 10             # Länge der Folge, Zahl der Elemente beziehungsweise Kanten
N_CAP = {"Schichtfolgen": 400, "Permutationen": 150, "Ordnungsbäume": 200}   # größtes n je Familie, das die App rechnet

ENUM_SHIFT_N = 12                                # Aufzählen aller Schichtfolgen bis hier (3^12 = 531.441)
ENUM_PERM_N = 8                                  # ... aller Permutationen bis hier
ENUM_TREE_N = 9                                  # ... aller Ordnungsbäume bis hier
DYCK_N = 60                                      # Dyck-Pfade nach Spitzen (zweiter Weg für die Blätter) bis hier

PERM_COMPARE_N = 10                              # Experiment 2: Permutationen von n Elementen
GROWTH_NS = (50, 100, 200, 400, 800)             # Experiment 3: Länge der Schichtfolge
NORMAL_SHIFT_NS = (10, 25, 50, 100, 200, 400)    # Experiment 4: Abstand zur Normalverteilung
NORMAL_OTHER_NS = (10, 50, 200)
EFFORT_NS = (100, 400, 1000)                     # Experiment 5
TIME_NS = (400, 1000)                            # ... gemessene Zeit (nur auf Klick, nicht getestet)
PLAY_N_MIN, PLAY_N_MAX, PLAY_N_DEFAULT = 4, 8, 7  # Spielwiese: Städte der Rundreise
PLAY_R = 5                                       # ... Kosten 1 bis 5
PLAY_SEED_MAX, PLAY_SEED_DEFAULT = 999999, 35

COLOR_MAIN = "#2F6B65"
COLOR_ALL = "rgba(150,150,150,0.75)"
COLOR_WARN = "#c0504d"
COLOR_LINE = "#4c78a8"

PRESETS = {
    "Standardfall: Nachtschichten, n = 10": {"stat": "Schichtfolgen: Nächte", "n": 10, "normal": "ja"},
    "Frühschichten, n = 20": {"stat": "Schichtfolgen: Frühschichten", "n": 20, "normal": "ja"},
    "Lange Folgen: Spätschichten, n = 400": {"stat": "Schichtfolgen: Spätschichten", "n": 400, "normal": "ja"},
    "Blätter von Ordnungsbäumen, n = 12": {"stat": "Ordnungsbäume: Blätter", "n": 12, "normal": "ja"},
    "Abstiege in Permutationen, n = 12": {"stat": "Permutationen: Abstiege", "n": 12, "normal": "ja"},
    "Inversionen in Permutationen, n = 12": {"stat": "Permutationen: Inversionen", "n": 12, "normal": "ja"},
    "Zyklen in Permutationen, n = 12": {"stat": "Permutationen: Zyklen", "n": 12, "normal": "nein"},
}
PRESET_HELP = {
    "Standardfall: Nachtschichten, n = 10": "Von den 13.926 gültigen Schichtfolgen der Länge 10 haben 1.024 keine Nacht und 4 sieben Nächte: Mittel 2,32, Varianz 1,66.",
    "Frühschichten, n = 20": "Wie sich die Frühschichten auf die gültigen Folgen der Länge 20 verteilen; nach einer Nacht ist keine Frühschicht erlaubt.",
    "Lange Folgen: Spätschichten, n = 400": "Mit 400 Schichten liegt die Verteilung glockenförmig um ihr Mittel; das Momenten-Semiring braucht dafür nur drei Zahlen je Zustand.",
    "Blätter von Ordnungsbäumen, n = 12": "Ordnungsbäume mit 12 Kanten nach Zahl der Blätter (Narayana-Zahlen): Mittel (n+1)/2 = 6,5.",
    "Abstiege in Permutationen, n = 12": "Eulersche Zahlen: Mittel (n−1)/2 = 5,5, Varianz (n+1)/12; die Verteilung ist symmetrisch.",
    "Inversionen in Permutationen, n = 12": "Mahonische Zahlen: Mittel n(n−1)/4 = 33, Varianz n(n−1)(2n+5)/72.",
    "Zyklen in Permutationen, n = 12": "Stirling-Zahlen erster Art: Mittel H₁₂ ≈ 3,10; die Verteilung ist schief, die Normalverteilung passt hier schlechter als bei den anderen Familien (Experiment 4).",
}
