"""PDF-Export der aktuellen Aufgabe mit den Rechenwegen und den ersten Werten (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

from zpm_evaluation import Analysis, distribution_rows, verdict_answers, way_rows

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "€": "EUR", "„": '"', "“": '"', "ⁿ": "^n", "²": "^2", "ₖ": "k", "∞": "unendlich",
            "⁻": "-", "⁰": "0", "¹": "1", "³": "3", "⁴": "4", "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "ₙ": "n"}


def _s(text) -> str:
    out = str(text)
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(a: Analysis) -> bytes:
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Zählen nach Parameter: Verteilung statt Gesamtzahl"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, _s(f"{a.settings.stat}, n = {a.n_eff}. Alles gerechnet, keine Messdaten."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.multi_cell(0, 5, _s(verdict_answers(a)[1]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    widths = (35, 65, 55, 20, 15)
    heads = ("Frage", "Weg", "Ergebnis", "Schritte", "Prüfung")
    for h, w in zip(heads, widths):
        pdf.cell(w, 6, _s(h), border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 8)
    for row in way_rows(a):
        for key, w in zip(heads, widths):
            pdf.cell(w, 5.5, _s(row[key])[:40], border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 9)
    for h, w in ((a.kind, 40), ("Anzahl", 70), ("Anteil in %", 30)):
        pdf.cell(w, 6, _s(h), border=1)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    for row in distribution_rows(a, 25):
        for key, w in ((a.kind, 40), ("Anzahl", 70), ("Anteil in %", 30)):
            pdf.cell(w, 5.5, _s(row[key])[:40], border=1)
        pdf.ln()
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Quelle: zaehlen-nach-parameter-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
