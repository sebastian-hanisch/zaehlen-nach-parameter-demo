"""Zählen nach Parameter – Verteilung statt Gesamtzahl - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 8 der Reihe „Abzählen und erzeugende Funktionen“: Die bivariate erzeugende Funktion zählt Strukturen zugleich nach Größe und nach einem Parameter. Die Zeilen sind die Verteilung (Nachtschichten,
Blätter, Abstiege, Inversionen, Zyklen), die Ableitungen bei y = 1 geben Mittel und Streuung (Momenten-Semiring); wie normal die Verteilung ist, ist eine Messung.
Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import math

import streamlit as st

import zpm_constants as C
from zpm_evaluation import (
    Settings,
    analyse,
    big_text,
    de,
    distribution_rows,
    effort_rows,
    frac_text,
    growth_rows,
    normality_rows,
    perm_compare,
    sci_text,
    time_experiment,
    tour_play,
    verdict_answers,
    verdict_effort,
    verdict_growth,
    verdict_normality,
    verdict_perm_compare,
    verdict_time,
    verdict_tour,
    way_rows,
)
from zpm_layout import dunkles_design, kopf_css
from zpm_pdf_export import build_pdf
from zpm_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    sidebar_presets,
    sync_query_params,
)
from zpm_visualization import build_distribution, build_effort, build_growth, build_normality, build_perm_compare


st.set_page_config(page_title="Zählen nach Parameter – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _perm_compare():
    return perm_compare()


@st.cache_data(show_spinner=False)
def _growth():
    return growth_rows()


@st.cache_data(show_spinner=False)
def _normality():
    return normality_rows()


@st.cache_data(show_spinner=False)
def _effort():
    return effort_rows()


@st.cache_data(show_spinner=False)
def _tour(n, seed):
    return tour_play(n, seed)


def verdict(pair):
    kind, text = pair
    getattr(st, kind)(text)


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in zpm_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("📊 Zählen nach Parameter – Verteilung statt Gesamtzahl")
st.markdown(
    """
**Die Gesamtzahl reicht nicht.** Wie viele der gültigen Schichtfolgen haben zwei, wie viele fünf Nachtschichten? Wie viele Ordnungsbäume haben drei Blätter? Eine zweite Variable $y$ zählt den **Parameter** mit:
$F(z, y) = \\sum c(n, k)\\, z^n y^k$ mit $c(n, k)$ = Zahl der Strukturen der Größe $n$ mit Parameterwert $k$. Die Zeile $k \\mapsto c(n, k)$ ist die **Verteilung**; aus den **Ableitungen bei $y = 1$** folgen Mittel und Varianz,
ohne die Verteilung zu speichern (ein **Momenten-Semiring** mit drei Zahlen je Zustand, ein weiteres Semiring im Sinn von Stück 4). Wie nah die Verteilung an einer Normalverteilung liegt, ist eine **Messung**.

Weiter unten: **fünf Experimente** (**🔬**), eine **🎲 Spielwiese**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert das Zählen nach Parameter", expanded=True):
    st.markdown(
        """
1. **Parameter wählen:** bei den Schichtfolgen die Zahl der Nächte (oder Früh- oder Spätschichten), bei den Ordnungsbäumen die Blätter, bei den Permutationen Abstiege, Inversionen oder Zyklen.
2. **Verteilung rechnen:** Auf dem Netz aus Stück 1 trägt jeder Zustand statt einer Zahl ein Polynom in $y$; jede Kante mit dem gezählten Buchstaben multipliziert mit $y$. Die bekannten Familien haben geschlossene Rechnungen (Narayana-Formel, Rekursion der Eulerschen Zahlen, Produkt der Mahonischen Zahlen, Dreieck der Stirling-Zahlen).
3. **Mittel und Streuung aus Ableitungen:** Mit $F_y(z, 1)$ und $F_{yy}(z, 1)$ bleiben je Zustand drei Zahlen: Zahl der Folgen, Summe der Parameter, Summe von $k(k-1)$. Mittel $= \\sum k\\, c / \\sum c$, Varianz $= \\sum k(k-1)\\, c / \\sum c + \\text{Mittel} - \\text{Mittel}^2$.
4. **Gegenproben:** Aufzählen aller Strukturen (klein), die Verteilung in Brüchen, Formeln für Mittel und Varianz (bekannte Familien); die Rechenwege müssen übereinstimmen.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Verteilung**")
    stat = st.selectbox("Struktur und Parameter", list(C.STATS), key="stat_select", help="Welche Strukturen gezählt werden und nach welchem Parameter die Verteilung gebildet wird.")
    n = st.slider("Größe n", *bounds("n_slider"), key="n_slider",
                  help=f"Länge der Schichtfolge, Zahl der Elemente der Permutation beziehungsweise Zahl der Kanten des Ordnungsbaums. Höchstens {', '.join(f'{k} ({v})' for k, v in C.N_CAP.items())}.")
    normal = st.selectbox("Normalverteilung einzeichnen", list(C.NORMAL_CHOICES), key="normal_select", help="Zeichnet die Normalverteilung mit gleichem Mittel und gleicher Varianz in das Diagramm.")

sync_query_params({"stat_select": stat, "n_slider": int(n), "normal_select": normal})

settings = Settings(stat, int(n), normal)
a = _analysis(settings)
for note in a.notes:
    st.info(note)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
total = sum(a.dist)
sd = math.sqrt(float(a.var))
mode = max(range(len(a.dist)), key=lambda k: (a.dist[k], -k))
m1, m2, m3, m4 = st.columns(4)
m1.metric("Gesamtzahl der Strukturen", big_text(total), help="Summe der Verteilung über alle Parameterwerte.")
m2.metric("Mittel", frac_text(a.mean), help=f"Mittlere Zahl der {a.kind}, exakt als Bruch gerechnet und gerundet.")
m3.metric("Standardabweichung", de(sd, 4), help="Wurzel der Varianz; die Varianz selbst steht im Text unten.")
m4.metric(f"Häufigster Wert ({a.kind})", str(mode), help="Der Parameterwert mit den meisten Strukturen (der kleinste, wenn es mehrere gibt).")
st.plotly_chart(build_distribution(a.dist, a.kind, show_normal=(normal == "ja")), width="stretch", key="main_chart")
st.caption("Anteil der Strukturen mit dem jeweiligen Parameterwert in Prozent (Balken), gestrichelt das Mittel; auf Wunsch die Normalverteilung mit gleichem Mittel und gleicher Varianz.")
with st.expander("Die Verteilung als Tabelle"):
    st.dataframe(distribution_rows(a), hide_index=True, width="stretch")

if st.button("📄 PDF der aktuellen Aufgabe erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(a))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="zaehlen-nach-parameter.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Was verrät die Verteilung, was die Gesamtzahl nicht verrät?")
verdict(verdict_answers(a))

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Dieselben Zahlen auf allen Wegen")
st.caption(f"Die eingestellte Aufgabe auf allen Wegen, die für sie gelten: die Verteilung (Polynom je Zustand, geschlossene Rechnung, zweite unabhängige Formel, Aufzählen bei kleinem n: Schichtfolgen bis n = {C.ENUM_SHIFT_N}, "
           f"Permutationen bis n = {C.ENUM_PERM_N}, Ordnungsbäume bis n = {C.ENUM_TREE_N}) und Mittel und Varianz (aus der Verteilung in Brüchen, Momenten-Semiring beim Automaten, Formel bei den bekannten Familien).")
if a.problems:
    st.error("Die Rechenwege widersprechen sich: " + "; ".join(a.problems))
else:
    st.success("Alle gerechneten Wege geben je Frage dieselbe Zahl.")
st.dataframe(way_rows(a), hide_index=True, width="stretch")

st.markdown("---")

st.subheader("🔬 Experiment 2: Gleiche Gesamtzahl, verschiedene Verteilung")
st.caption(f"Dieselben Permutationen von {C.PERM_COMPARE_N} Elementen, dreimal nach einem anderen Parameter gezählt: Abstiege, Inversionen, Zyklen. Die Gesamtzahl ist jedes Mal {C.PERM_COMPARE_N}!.")
cmp_rows = _perm_compare()
st.plotly_chart(build_perm_compare(cmp_rows), width="stretch", key="compare_chart")
st.dataframe([{"Statistik": r["Statistik"], "Gesamtzahl": big_text(r["Gesamtzahl"]), "Mittel": frac_text(r["Mittel"], 4), "Varianz": frac_text(r["Varianz"], 4), "Standardabweichung": de(r["Standardabweichung"], 4),
               "kleinster Wert": r["kleinster Wert"], "größter Wert": r["größter Wert"]} for r in cmp_rows], hide_index=True, width="stretch")
verdict(verdict_perm_compare(cmp_rows))

st.markdown("---")

st.subheader("🔬 Experiment 3: Mittel und Streuung wachsen mit n")
st.caption("Schichtfolgen, Zahl der Nächte: Mittel und Varianz aus dem Momenten-Semiring für n = 50 bis 800 und der Zuwachs je Schritt, gegen die Ableitungen des größten Eigenwerts der Übergangsmatrix (Stück 2).")
growth = _growth()
st.plotly_chart(build_growth(growth), width="stretch", key="growth_chart")
st.dataframe([{"n": r["n"], "Mittel": frac_text(r["Mittel"], 4), "Varianz": frac_text(r["Varianz"], 4), "Zuwachs Mittel je Schritt": frac_text(r["Zuwachs Mittel"], 6), "Zuwachs Varianz je Schritt": frac_text(r["Zuwachs Varianz"], 6)} for r in growth["rows"]],
             hide_index=True, width="stretch")
verdict(verdict_growth(growth))

st.markdown("---")

st.subheader("🔬 Experiment 4: Wie normal ist die Verteilung?")
st.caption("Größter Abstand zwischen der Verteilungsfunktion und der Normalverteilung mit gleichem Mittel und gleicher Varianz (Stetigkeitskorrektur), je Familie und Größe. Das ist eine Messung, kein Satz.")
norm_rows = _normality()
st.plotly_chart(build_normality(norm_rows), width="stretch", key="normality_chart")
st.dataframe([{"Familie": r["Familie"], "n": r["n"], "Abstand": de(r["Abstand"], 5), "Abstand mal √n": de(r["Abstand"] * math.sqrt(r["n"]), 4)} for r in norm_rows], hide_index=True, width="stretch")
verdict(verdict_normality(norm_rows))

st.markdown("---")

st.subheader("🔬 Experiment 5: Aufwand")
st.caption("Schichtfolgen, Zahl der Nächte: Additionen der Verteilung (ein Polynom je Zustand) gegen die des Momenten-Semirings (drei Zahlen je Zustand), nach der Zählregel der Demo gezählt (das Semiring drei Additionen je Übergang). Die Zeit messen Sie auf Klick; sie ist eine Messung dieses Rechners.")
effort = _effort()
st.plotly_chart(build_effort(effort), width="stretch", key="effort_chart")
st.dataframe([{"n": r["n"], "Werte der Verteilung": r["Werte der Verteilung"], "Stellen der Gesamtzahl": r["Stellen der Gesamtzahl"], "Additionen Verteilung": big_text(r["Additionen Verteilung"]),
               "Additionen Momente": big_text(r["Additionen Momente"]), "Faktor": de(r["Faktor"], 1), "gleiches Mittel und gleiche Varianz": "ja" if r["gleiches Mittel und gleiche Varianz"] else "nein"} for r in effort],
             hide_index=True, width="stretch")
verdict(verdict_effort(effort))
if st.button("⏱️ Zeit messen", key="time_run"):
    st.session_state["time_res"] = time_experiment()
timing = st.session_state.get("time_res")
if timing:
    st.dataframe([{"n": r["n"], "Verteilung (Sekunden)": de(r["Verteilung (Sekunden)"], 3), "Momente (Sekunden)": de(r["Momente (Sekunden)"], 4)} for r in timing], hide_index=True, width="stretch")
    verdict(verdict_time(timing))

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------

st.subheader("🎲 Spielwiese: Kostenverteilung einer Rundreise")
st.caption(f"Eine zufällige Rundreise-Aufgabe (vollständiger Digraph, Kosten 1 bis {C.PLAY_R}, Stück 7): Wie verteilen sich die Gesamtkosten aller Hamiltonkreise ab Stadt 0? Das Mittel ist die Summe aller Kantenkosten durch n − 1.")
q1, q2 = st.columns(2)
play_n = q1.slider("Städte n", C.PLAY_N_MIN, C.PLAY_N_MAX, C.PLAY_N_DEFAULT, key="play_n", help="Zahl der Städte; bei 8 Städten sind es 5.040 Rundreisen.")
play_seed = q2.number_input("Seed der Kosten", 0, C.PLAY_SEED_MAX, C.PLAY_SEED_DEFAULT, key="play_seed", step=1)
tour = _tour(int(play_n), int(play_seed))
st.plotly_chart(build_distribution(tour["dist"], "Kosten", show_normal=(normal == "ja"), title="Anteil der Rundreisen in %"), width="stretch", key="tour_chart")
verdict(verdict_tour(tour))

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    f"""
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Ein Parameter** | Die App zählt nach genau einem Parameter; zwei Parameter zugleich (zum Beispiel Nächte und Frühschichten) brauchen eine Reihe in drei Variablen und liefern eine gemeinsame Verteilung, nicht zwei Verteilungen. | – |
| **Mittel und Streuung genügen** | Die Gesamtzahl verrät nichts über die Form (Experiment 2); auch Mittel und Varianz sagen nichts über Schiefe und Ränder. Die App zeigt deshalb die ganze Verteilung. | – |
| **Die Verteilung ist fast normal** | Bei den Abstiegen und Blättern fällt der Abstand schnell, bei den Zyklen der Permutationen bis n = 200 nicht erkennbar (Experiment 4): die Varianz wächst dort nur logarithmisch. Gemessen bis n = 400 beziehungsweise 200, kein Satz. | Stück 9 der Reihe: Asymptotik |
| **Genau gezählt** | Die Verteilung ist exakt (ganze Zahlen, Brüche für Mittel und Varianz). Wer Wahrscheinlichkeiten braucht, teilt durch die Gesamtzahl; das tut die App nur für die Anzeige. | – |
| **Der Automat ist der aus Stück 1** | Andere Regeln geben andere Verteilungen; die Eigenwertrechnung (Experiment 3) gilt für diesen Automaten. | Stück 1 und 2 |
| **Größe begrenzt** | Schichtfolgen bis n = {C.N_CAP['Schichtfolgen']}, Permutationen bis {C.N_CAP['Permutationen']}, Ordnungsbäume bis {C.N_CAP['Ordnungsbäume']}; darüber wird gekappt und das gesagt. | – |
| **Zufallsziehen** | Aus einer Verteilung gezielt Strukturen mit vorgegebenem Parameter ziehen ist ein eigenes Thema. | Stück 10 der Reihe |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Bivariate erzeugende Funktion.** Für eine Klasse von Strukturen mit Größe $n$ und Parameter $k$ sei $c(n,k)$ ihre Zahl und $F(z, y) = \sum_{n,k} c(n,k)\, z^n y^k$. Die Zeile $c(n, \cdot)$ ist die Verteilung des Parameters bei Größe $n$; $F(z, 1)$ zählt die Gesamtzahl.

**Mittel und Varianz.** Mit $N_n = [z^n] F(z, 1)$, $M_n = [z^n] F_y(z, 1)$ und $Q_n = [z^n] F_{yy}(z, 1)$ ist
$$\mathbb{E}[k] = \frac{M_n}{N_n}, \qquad \operatorname{Var}[k] = \frac{Q_n}{N_n} + \frac{M_n}{N_n} - \Big(\frac{M_n}{N_n}\Big)^2.$$
Im Netz (Stück 4) trägt jeder Zustand das Tripel $(N, M, Q)$; ein Schritt mit Gewicht $y^w$ wirkt als $(N, M, Q) \mapsto (N,\; M + wN,\; Q + 2wM + w(w-1)N)$, Summen addieren die Tripel.

**Schichtautomat.** Die Übergangsmatrix $T(y)$ hat Gewicht $y$ auf den Kanten mit dem gezählten Buchstaben. Für den größten Eigenwert $\lambda(y)$ ist die mittlere Zahl je Schritt $\mu = \frac{d \ln \lambda}{d \ln y}\big|_{y=1}$ und die Varianz je Schritt $\sigma^2 = \frac{d^2 \ln \lambda(e^t)}{dt^2}\big|_{t=0}$.

**Bekannte Familien.** Ordnungsbäume nach Blättern: Narayana-Zahlen $N(n,k) = \frac{1}{n}\binom{n}{k}\binom{n}{k-1}$ mit Mittel $\frac{n+1}{2}$ und Varianz $\frac{n^2 - 1}{4(2n-1)}$. Permutationen nach Abstiegen (Eulersche Zahlen): Mittel $\frac{n-1}{2}$, Varianz $\frac{n+1}{12}$.
Nach Inversionen (Mahonische Zahlen, Koeffizienten von $\prod_{i=1}^{n} (1 + q + \dots + q^{i-1})$): Mittel $\frac{n(n-1)}{4}$, Varianz $\frac{n(n-1)(2n+5)}{72}$. Nach Zyklen (Stirling-Zahlen erster Art): Mittel $H_n$, Varianz $H_n - H_n^{(2)}$.

**Abstand zur Normalverteilung.** $D = \max_k \big| F_n(k) - \Phi\big((k + \tfrac12 - \mu)/\sigma\big) \big|$ mit der Verteilungsfunktion $F_n$ der Strukturen und der Normalverteilung $\Phi$ mit gleichem Mittel und gleicher Varianz.

**Literatur** (Titel und Fundstelle aus dem Gedächtnis, nicht eingesehen).
P. Flajolet und R. Sedgewick: *Analytic Combinatorics*, Cambridge University Press, 2009 (bivariate erzeugende Funktionen, Mittel und Varianz aus Ableitungen, Grenzwertsätze).
E. A. Bender: *Central and local limit theorems applied to asymptotic enumeration*, Journal of Combinatorial Theory A 15, 1973, S. 91–111 (Normalverteilung für Parameter von Strukturen).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Abzählen: von der Rekursion zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-abzaehlen.html)."
)
