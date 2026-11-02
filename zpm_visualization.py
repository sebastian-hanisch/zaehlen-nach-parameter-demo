"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import math

import plotly.graph_objects as go

import zpm_algorithm as A
import zpm_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _normal_curve(xs, mu, sd, total):
    return [total * math.exp(-0.5 * ((x - mu) / sd) ** 2) / (sd * math.sqrt(2 * math.pi)) for x in xs] if sd > 0 else [0.0] * len(xs)


def build_distribution(dist, kind: str, show_normal: bool = True, title: str = "Anteil in %"):
    """Verteilung als Balken (Anteil in Prozent); wahlweise mit der Normalverteilung gleichen Mittels und gleicher Varianz."""
    total = sum(dist)
    ks = [k for k, c in enumerate(dist) if c]
    mean, var = A.mean_var(dist)
    mu, sd = float(mean), math.sqrt(float(var))
    fig = go.Figure()
    fig.add_trace(go.Bar(x=ks, y=[100 * dist[k] / total for k in ks], name="exakt", marker_color=C.COLOR_MAIN))
    if show_normal and sd > 0:
        xs = [ks[0] + i * (ks[-1] - ks[0]) / 200 for i in range(201)] if ks[-1] > ks[0] else ks
        fig.add_trace(go.Scatter(x=xs, y=[100 * v for v in _normal_curve(xs, mu, sd, 1.0)], mode="lines", name="Normalverteilung", line=dict(color=C.COLOR_WARN, width=2)))
    fig.add_vline(x=mu, line=dict(color=C.COLOR_ALL, dash="dash"))
    fig.update_xaxes(title_text=f"Zahl der {kind}")
    fig.update_yaxes(title_text=title)
    return _base(fig, 340)


def build_perm_compare(rows: list[dict]):
    """Die drei Statistiken derselben Permutationen: Anteil in Prozent je Parameterwert."""
    fig = go.Figure()
    colors = (C.COLOR_MAIN, C.COLOR_LINE, C.COLOR_WARN)
    for row, color in zip(rows, colors):
        total = row["Gesamtzahl"]
        d = row["dist"]
        fig.add_trace(go.Scatter(x=list(range(len(d))), y=[100 * c / total for c in d], mode="lines+markers", name=row["Statistik"], line=dict(color=color)))
    fig.update_xaxes(title_text="Wert der Statistik")
    fig.update_yaxes(title_text="Anteil der Permutationen in %")
    return _base(fig, 340)


def build_growth(res: dict):
    """Mittel und Varianz der Nächte gegen die Länge n (beide wachsen linear)."""
    rows = res["rows"]
    fig = go.Figure()
    ns = [r["n"] for r in rows]
    fig.add_trace(go.Scatter(x=ns, y=[float(r["Mittel"]) for r in rows], mode="lines+markers", name="Mittel", line=dict(color=C.COLOR_MAIN)))
    fig.add_trace(go.Scatter(x=ns, y=[float(r["Varianz"]) for r in rows], mode="lines+markers", name="Varianz", line=dict(color=C.COLOR_LINE)))
    fig.update_xaxes(title_text="Länge n der Schichtfolge")
    fig.update_yaxes(title_text="Nächte")
    return _base(fig, 320)


def build_normality(rows: list[dict]):
    """Abstand zur Normalverteilung gegen n, je Familie eine Linie (logarithmische Achsen)."""
    fig = go.Figure()
    colors = {"Nachtschichten": C.COLOR_MAIN, "Eulersche Zahlen (Abstiege)": C.COLOR_LINE, "Narayana (Blätter)": C.COLOR_ALL, "Stirling erster Art (Zyklen)": C.COLOR_WARN}
    for name in dict.fromkeys(r["Familie"] for r in rows):
        sub = [r for r in rows if r["Familie"] == name]
        fig.add_trace(go.Scatter(x=[r["n"] for r in sub], y=[r["Abstand"] for r in sub], mode="lines+markers", name=name, line=dict(color=colors[name])))
    fig.update_xaxes(title_text="n", type="log")
    fig.update_yaxes(title_text="Abstand zur Normalverteilung", type="log")
    return _base(fig, 340)


def build_effort(rows: list[dict]):
    """Additionen der Verteilung gegen die des Momenten-Semirings (Zehnerlogarithmus)."""
    fig = go.Figure()
    names = [str(r["n"]) for r in rows]
    fig.add_trace(go.Bar(x=names, y=[math.log10(r["Additionen Verteilung"]) for r in rows], name="Verteilung", marker_color=C.COLOR_ALL))
    fig.add_trace(go.Bar(x=names, y=[math.log10(r["Additionen Momente"]) for r in rows], name="Momenten-Semiring", marker_color=C.COLOR_MAIN))
    fig.update_layout(barmode="group")
    fig.update_xaxes(title_text="Länge n")
    fig.update_yaxes(title_text="Additionen (Zehnerlogarithmus)")
    return _base(fig, 320)
