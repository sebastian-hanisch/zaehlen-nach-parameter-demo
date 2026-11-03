# Zählen nach Parameter – Verteilung statt Gesamtzahl – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-zaehlen-nach-parameter-demo.streamlit.app/)**

Stück 8 von 16 der Reihe **„Abzählen und erzeugende Funktionen“** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (die Linie wird erst vollständig veröffentlicht). Vorgänger sind `aufzaehlen-rekursion-demo` (Stück 1), `rationale-ef-demo` (Stück 2), `symbolische-methode-demo` (Stück 3), `semiring-rekursion-demo` (Stück 4), `multimengen-partitionen-demo` (Stück 5), `beschriftete-strukturen-demo` (Stück 6) und `siebformel-demo` (Stück 7); sie haben **eine Zahl** geliefert, die Gesamtzahl. Diese Demo zählt **nach einem Parameter**: Eine zweite Variable y der erzeugenden Funktion zählt mit, die Zeilen der bivariaten Reihe sind die **Verteilung** (Nachtschichten einer Schichtfolge, Blätter eines Ordnungsbaums, Abstiege, Inversionen und Zyklen einer Permutation), und die **Ableitungen bei y = 1** geben Mittel und Streuung, ohne die Verteilung zu speichern (ein Momenten-Semiring mit drei Zahlen je Zustand). Wie nah die Verteilung an einer Normalverteilung liegt, ist eine **Messung**.

## Warum dieses Problem

Wer plant, braucht oft mehr als die Gesamtzahl: wie viele der gültigen Schichtfolgen haben zwei, wie viele fünf Nachtschichten; wie sich die Kosten aller Rundreisen verteilen. Die Gesamtzahl verrät nichts über die Form: dieselben 3.628.800 Permutationen von 10 Elementen haben je nach Statistik ganz verschiedene Verteilungen. Die Demo zeigt die Rechnung (Verteilung und Momenten-Semiring), ihre Gegenproben, wie Mittel und Streuung beim Automaten wachsen, und wo die Normalnäherung gut und wo schlecht ist.

## Befunde und Korrekturen gegenüber dem Plan

- **Hook bestätigt:** Bivariate Reihe, Verteilung der Nachtschichten und der Blätter, Mittel und Streuung aus Ableitungen; Blätter sind die Narayana-Zahlen, Nachtschichten laufen auf dem Automaten aus Stück 1.
- **Phase-0-Zahl für die Zyklen war falsch (mein Fehler im Messskript):** Das Skript hatte die Verteilung der Zyklen um einen Index verschoben und für n = 10 den Mittelwert 1,93 gemeldet. Richtig ist **H₁₀ = 7381/2520 ≈ 2,9290** (Träger 1 bis 10, nicht 0 bis 9); die Varianz 1,3792 war schon richtig. Der Test prüft Mittel und Varianz gegen H_n und H_n − H_n^(2) für n = 2 bis 60.
- **Aufwand genauer gezählt:** Phase 0 schätzte bei n = 1000 etwa 2 Millionen Additionen für die Verteilung und 36.000 für das Momenten-Semiring. Gezählt werden **3.002.995** und **29.980**, also etwa **100-mal weniger** (nicht 56-mal). Gezählt sind die im Code tatsächlich ausgeführten Additionen: eine je Polynomkoeffizient und Kante bei der Verteilung, fünf je Übergang beim Semiring (a + c; b + s₁ + w·c; d + s₂ + 2·w·s₁, auch bei w = 0 ausgeführt); die abschließende Summation über die Zustände zählt nicht mit, Multiplikationen auch nicht. Ein früherer Stand zählte nur drei je Übergang (17.988, Faktor 167); `tests/test_op_counts.py` vergleicht beide Zähler mit einer unabhängigen Zählung im ausgeführten Code. Die Laufzeit ist davon getrennt eine Messung (n = 1000: 137-mal in der Messung unten, 117-mal in einem unabhängigen Nachlauf).
- **Gegenbefund zur Normalverteilung:** Bei den Zyklen der Permutationen fällt der Abstand zur Normalverteilung bis n = 200 nicht (0,0254, 0,0286, 0,0253 für n = 10, 50, 200), bei den Nachtschichten, Abstiegen und Blättern fällt er schnell. Für sehr große n fällt er auch bei den Zyklen, nur extrem langsam (nach einer unabhängigen Nachrechnung 0,0174 bei n = 10⁶). Das gilt für die gerechneten Größen, ist kein Satz.
- **Eigenwert und Zuwachs stimmen:** Zuwachs von Mittel und Varianz je Schritt ab n = 50 auf sechs Stellen konstant (0,215835 und 0,154569), gleich den Ableitungen des größten Eigenwerts 2,546818 aus Stück 2.
- **Präfix:** `prm_` aus dem Plan gehört `permutation-test-demo`; die Demo nutzt `zpm_`. Port 9321 wie geplant.
- **Falsche Handrechnung (meine, nicht der Code):** In einem Test hatte ich den Kolmogorov-Abstand von zwei gleich häufigen Werten mit 0 statt 1 − Φ(2) ≈ 0,0228 erwartet (das Maximum liegt bei k = 1); in einem anderen eine gerundete Konstante mit zu enger Toleranz (n = 80 liegt noch 7·10⁻⁹ daneben). Beides im Test korrigiert, der Code war richtig.

## Modell

Eine **Verteilung** ist eine Liste `d`: d[k] = Zahl der Strukturen mit Parameterwert k. `shift_distribution` rechnet sie für den Schichtautomaten aus Stück 1 (Zustand = Zahl der Nächte am Ende, ein Polynom je Zustand, jede Kante mit dem gezählten Buchstaben multipliziert mit y); `shift_moments` rechnet dasselbe als Momenten-Semiring (je Zustand drei Zahlen: Zahl der Folgen, Summe der Parameter, Summe von k(k−1)). Die bekannten Familien haben geschlossene Rechnungen: `narayana` (Blätter der Ordnungsbäume), `eulerian` (Abstiege), `mahonian` (Inversionen), `stirling1_row` (Zyklen), jeweils mit einem zweiten Weg (`dyck_peaks`, `eulerian_formula`, `stirling1_polynomial`). `mean_var` und `mean_var_moments` rechnen Mittel und Varianz in Brüchen, `kolmogorov_distance` den Abstand zur Normalverteilung, `shift_growth` die Wachstumsraten aus dem größten Eigenwert. Die Formeln stehen im 📐-Expander der App.

## Methodik

- **Rechenwege in der App** (Experiment 1): Verteilung: Polynom je Zustand (DP) gegen Aufzählen aller Folgen (bis n = 12); bei den Bäumen die Formel gegen die Dyck-Pfad-DP (bis n = 60) und das Aufzählen aller Ordnungsbäume (bis n = 9); bei den Permutationen die Rekursion gegen eine unabhängige Formel (Abstiege, Zyklen) und das Aufzählen aller Permutationen (bis n = 8). Mittel und Varianz: aus der Verteilung (Brüche), Momenten-Semiring (Automat), Formel (bekannte Familien). Bei Abweichung zeigt die App einen Fehler statt einer Zahl.
- **Aufwand** wird als Zahl der im Code ausgeführten Additionen gezählt (getestet gegen eine unabhängige Zählung); die Zeit steht nur als Messung auf Klick.
- **Eingabe:** Struktur und Parameter (sieben Möglichkeiten), Größe n (je Familie begrenzt auf 400, 150 und 200), Normalverteilung einzeichnen (ja oder nein). Die Adresszeile spiegelt die Einstellung.

## Befunde (gemessen, keine Behauptungen)

Jede Zahl steht in `tests/test_claims.py`, `tests/test_algorithm.py`, `tests/test_verdicts.py` oder `tests/test_oracle_zpm.py`. Zeiten stehen in keinem Test; sie sind gemessen und gekennzeichnet.

| Frage | Befund |
|---|---|
| Handinstanzen | Schichtfolgen der Länge 3 nach Nächten: 8, 8, 4 (zusammen 20, gleich Stück 4), nach Frühschichten 7, 8, 4, 1, nach Spätschichten 3, 10, 6, 1; Momenten-Semiring (20, 16, 8); Narayana n = 3: 1, 3, 1; Eulersche Zahlen n = 4: 1, 11, 11, 1; Mahonische Zahlen n = 3: 1, 2, 2, 1; Stirling erster Art n = 4: 6, 11, 6, 1 |
| Standardfall (Experiment 1) | Schichtfolgen der Länge 10 nach Nächten: 1.024, 2.816, 4.096, 3.472, 1.852, 571, 91, 4 (zusammen 13.926); Mittel 2,3166, Varianz 1,6581, Standardabweichung 1,2877; am häufigsten 2 Nächte mit 29,41 %; gleich dem Aufzählen (n ≤ 12) und dem Momenten-Semiring (Brüche) |
| Bekannte Verteilungen gegen ihre Formeln, n = 2 bis 60 (exakt in Brüchen) | Narayana (Blätter): Mittel (n+1)/2, Varianz (n²−1)/(4(2n−1)); Eulersche Zahlen (Abstiege): (n−1)/2, (n+1)/12; Mahonische Zahlen (Inversionen): n(n−1)/4, n(n−1)(2n+5)/72; Stirling erster Art (Zyklen): H_n, H_n − H_n^(2); Aufzählen aller Permutationen (n ≤ 8) und aller Ordnungsbäume (n ≤ 9) bestätigt die Verteilungen |
| Gleiche Gesamtzahl, verschiedene Verteilung (Experiment 2), n = 10 | 3.628.800 Permutationen: Abstiege Mittel 9/2, Varianz 11/12 (Träger 0 bis 9); Inversionen 45/2, 125/4 (0 bis 45); Zyklen 7381/2520 ≈ 2,9290, 350339/254016 ≈ 1,3792 (1 bis 10) |
| Wachstum beim Automaten (Experiment 3) | n = 50, 100, 200, 400, 800: Mittel 10,95, 21,74, 43,33, 86,49, 172,83; Varianz 7,84, 15,57, 31,03, 61,94, 123,77; Zuwachs je Schritt 0,215835 und 0,154569; größter Eigenwert 2,546818, μ = 0,21583, σ² = 0,15457 |
| Abstand zur Normalverteilung (Experiment 4), Kolmogorov mit Stetigkeitskorrektur | Nachtschichten n = 10, 25, 50, 100, 200, 400: 0,01324, 0,00946, 0,00671, 0,00467, 0,00324, 0,00230 (mal √n etwa 0,042 bis 0,047); Eulersche Zahlen n = 10, 50, 200: 0,00923, 0,00190, 0,00049; Narayana: 0,00554, 0,00124, 0,00031; Stirling erster Art: 0,02544, 0,02858, 0,02533 |
| Log-Konkavität | c_k² ≥ c_(k−1)·c_(k+1) in allen gerechneten Verteilungen: Nachtschichten n = 1 bis 200, Narayana und Eulersche Zahlen n = 2 bis 200, Stirling erster Art n = 2 bis 100, Mahonische Zahlen n = 2 bis 60 |
| Aufwand (Experiment 5) | n = 100, 400, 1000: Verteilung mit 68, 268, 668 Werten (Gesamtzahl 41, 163, 407 Stellen); Additionen Verteilung 30.295, 481.195, 3.002.995; Momenten-Semiring 2.980, 11.980, 29.980 (5·(3 + 5 + 6·(n−2))); Faktor 10,2, 40,2, 100,2; gleiches Mittel und gleiche Varianz |
| Kostenverteilung einer Rundreise (Spielwiese), 7 Städte, Kosten 1 bis 5, Seed 35 | 720 Rundreisen mit Kosten von 10 bis 33; Mittel 19 = Summe aller Kantenkosten 114 geteilt durch n − 1 = 6, Varianz 43/3 ≈ 14,333; bei 8 Städten 5.040 Rundreisen |
| Presets | Nachtschichten n = 10: 1.024 Folgen ohne Nacht, 4 mit sieben Nächten; Blätter n = 12: 208.012 Bäume, Mittel 6,5; Abstiege n = 12: Mittel 5,5, Varianz 13/12; Inversionen n = 12: Mittel 33; Zyklen n = 12: Mittel H₁₂ ≈ 3,10; Spätschichten n = 400: Gesamtzahl 3,04·10¹⁶² (163 Stellen), häufigster Wert 190 |
| Zeit (nur gemessen, **nicht getestet**) | Auf dem Entwicklungsrechner (Phase 0): n = 1000: Verteilung 0,96 s, Momenten-Semiring 0,007 s; die App misst n = 400 und 1000 auf Klick |

## Ehrliche Grenzen

- **Literaturwerte aus dem Gedächtnis:** Die Formeln für Mittel und Varianz (Narayana, Eulersche, Mahonische, Stirling) und die Grenzwertsätze wurden nicht an einer Quelle gelesen. Brüche bis n = 60 und Aufzählen stützen die Formeln; das ersetzt keine Quelle.
- **„Normal“ ist eine Messung:** Abstände nur bis n = 400 (Nachtschichten) beziehungsweise 200; der Text sagt „der Abstand fällt“ oder „fällt bis n = 200 nicht“, nie „strebt gegen 0“. Der Stirling-Gegenbefund gilt für n ≤ 200.
- **Log-Konkavität ist nur gemessen**, nicht bewiesen.
- **Ein Parameter, ein Automat:** Die Schichtfolgen zählen nach den Buchstaben N, F oder S des Automaten aus Stück 1; andere Parameter (zum Beispiel die Zahl der Wechsel) brauchen einen anderen Automaten.
- **Zwei Wörter für Streuung:** die App zeigt Varianz (exakt als Bruch) und Standardabweichung (Wurzel, Gleitkomma).
- **Aufzählen als Prüfer ist begrenzt** (Schichtfolgen n ≤ 12, Permutationen n ≤ 8, Ordnungsbäume n ≤ 9); darüber prüfen sich die Verteilungen gegenseitig (DP, Formel, Dyck-Pfade, steigendes Produkt), und das Momenten-Semiring gegen die Verteilung in Brüchen.
- **Aufwand als Additionen**, nicht als Zeit; die Zeiten sind Python-Messungen dieses Rechners.
- **Zielgröße begrenzt** (Schichtfolgen 400, Permutationen 150, Ordnungsbäume 200); darüber wird gekappt und das gesagt.
- **Browser:** Seitentext, Zahlen, Diagrammbreiten, Preset-Klick und die Zeitmessung im Browser geprüft; Handy-Breite nicht.
- Alles gerechnet, keine echten Daten.

## Verifikation

- **Kern:** Handinstanzen (Schichtfolgen n = 3 für N, F, S; Ordnungsbäume n = 3; Permutationen n = 3 und 4; Kolmogorov-Abstand von zwei Werten), Aufzählen aller Folgen, Permutationen und Ordnungsbäume, Brüche statt Momenten-Semiring, alternierende Summe und steigendes Produkt, Dyck-Pfad-DP, Potenzverfahren für den Eigenwert, Zählung der Übergänge von Hand (3, 5, 6 je Schritt), die Zustandsrekursion für die Gesamtzahl.
- **Eigenschaften:** Gesamtzahlen gleich n! beziehungsweise Catalan; Symmetrie der Eulerschen, Mahonischen und Narayana-Zahlen; lückenloser Träger; Log-Konkavität; Mittel im Träger und Varianz nichtnegativ; Varianz der Mahonischen Zahlen als Summe der Varianzen gleichverteilter Größen; die mittleren Zahlen von F, S und N ergeben n; konstante Zuwächse; Abstand fällt bei Automat und Eulerschen Zahlen, nicht bei den Zyklen; gleiches Ergebnis in Prozessen mit verschiedenem `PYTHONHASHSEED`.
- **Randfälle:** n = 0, 1, 2, Verteilung mit nur einem Wert, Formel bei n = 1 ausgelassen, Kappung je Familie mit Hinweis, Zahlen über der 4300-Stellen-Grenze nur formatiert, Bruch- und Gleitkommaformatierung, Verteilungstabelle gefenstert, Spielwiese mit Grenzwerten, jede Statistik bei den kleinsten Größen.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an Minimum und Maximum), alle Experimente, Permalink mit Müll und Grenzwerten, Kappung, jedes Preset, jede Statistik bei n = 1, 7, 30, Spielwiese, PDF an den Rändern; Footer-Test.
- **Layout:** Schnellstart oben in der Seitenleiste, fester Kopf, aktives Preset hervorgehoben; jede Änderung eines Reglers hebt die Markierung auf (`tests/test_layout.py`).
- **Nicht gemacht:** Mutationstests (seit 2026-10-28 nicht mehr verlangt), Docker-Lauf der Linux-CI (Docker fehlt auf diesem Rechner; die CI nach dem Push entscheidet).

429 Tests (`pytest tests`), zuletzt in etwa einer Minute (55 Sekunden gemessen) auf dem Entwicklungsrechner (Messung, nicht getestet).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, fünf Experimente, Spielwiese, Grenzen, Formeln |
| `zpm_algorithm.py` | Kern: Verteilungen, Momenten-Semiring, bekannte Familien, Mittel und Varianz, Abstand zur Normalverteilung, Eigenwert |
| `zpm_constants.py` | Regler-Grenzen, Schwellen, Farben, Presets |
| `zpm_evaluation.py` | Analyse, Experimente, Verdikte, Formatierung |
| `zpm_layout.py` | Fester Kopf (Stylesheet) |
| `zpm_pdf_export.py` | PDF der aktuellen Aufgabe (fpdf2) |
| `zpm_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste, aktives Preset hervorgehoben) |
| `zpm_scenario.py` | Familie und Parameter aus der Auswahl, Kappung, Kostenverteilung der Rundreise |
| `zpm_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Handwerte, Orakel, Eigenschaften, Randfälle, Verdikte, Claims, Zählung gegen Rechnung, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Beweise der Grenzwertsätze, lokale Grenzwertsätze, Quasi-Potenzen, reelle Nullstellen der Polynome (Frobenius):** Stück 9, Asymptotik; hier nur Messung.
- **Mehrere Parameter zugleich, höhere Momente und Schiefe als Satz, Extremwertverteilungen:** nicht Teil der Demo.
- **Gezieltes Ziehen mit vorgegebenem Parameter:** Stück 10, gleichverteilt ziehen.
- **Symmetrien und Polynome (Burnside, Tutte):** Stück 11 bis 14.
- **Verwandte Demos:** `semiring-rekursion-demo` (Semiring-Gedanke), `beschriftete-strukturen-demo` (Stirling-Zeilen), `siebformel-demo` (Kostenpolynom des TSP), `symbolische-methode-demo` (Ordnungsbäume), `aufzaehlen-rekursion-demo` (Schichtautomat); nur Verweise.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Streamlit Cloud: Python-Version nach der Voreinstellung der Plattform (lokal `3.14`, CI `3.12`); der Code nutzt nur Merkmale, die in `3.12` laufen.

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Abzählen: von der Rekursion zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-abzaehlen.html).
