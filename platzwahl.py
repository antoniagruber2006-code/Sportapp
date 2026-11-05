"""
Schritt 2: Platzwahl

- Schwarz = Platz ist im gewählten Zeitraum verfügbar
- Grau    = Platz ist im gewählten Zeitraum nicht verfügbar (gebucht/gesperrt)
- Rot     = aktuell gewählter Platz

Datum und Uhrzeit kommen aus Schritt 1 (st.session_state.datum / start / ende).
"""

from html import escape
from pathlib import Path
import tempfile

import streamlit as st
import streamlit.components.v1 as components

from daten import ist_verfuegbar, lade_reservierungen

# ---------------------------------------------------------------------------
# 1) Grundriss (alle Maße in Metern, nur beispielhaft -> beliebig änderbar)
# ---------------------------------------------------------------------------
# Ein Tennisplatz (Spielfeld) ist ca. 24 m x 11 m groß -> alle Plätze sind gleich groß.
PLATZ_B, PLATZ_H = 24, 11

RAND = 4  # Rand um den Plan
HALLE_B, HALLE_H = 116, 48  # Indoor- und Outdoor-Fläche sind gleich groß
INDOOR_Y = 6
OUTDOOR_Y = INDOOR_Y + HALLE_H + 4
PLAN_B = HALLE_B + 2 * RAND
PLAN_H = OUTDOOR_Y + HALLE_H + RAND

SPALTEN = 4  # Plätze pro Reihe
INDOOR_REIHEN = 2
OUTDOOR_REIHEN = 3
SERVICE_H = 14  # Höhe des Bereichs mit Rezeption, Umkleide, WC (nur Indoor)


def erzeuge_plaetze():
    """Erzeugt alle Plätze als gleich große Rechtecke: Name -> (x, y, Breite, Höhe)."""
    plaetze = {}
    abstand_x = (HALLE_B - SPALTEN * PLATZ_B) / (SPALTEN + 1)

    def reihen(prefix, y_oben, hoehe, anzahl_reihen):
        abstand_y = (hoehe - anzahl_reihen * PLATZ_H) / (anzahl_reihen + 1)
        nr = 1
        for r in range(anzahl_reihen):
            for c in range(SPALTEN):
                x = RAND + abstand_x + c * (PLATZ_B + abstand_x)
                y = y_oben + abstand_y + r * (PLATZ_H + abstand_y)
                plaetze[f"Platz {prefix}.{nr:02d}"] = (x, y, PLATZ_B, PLATZ_H)
                nr += 1

    reihen(1, INDOOR_Y + SERVICE_H, HALLE_H - SERVICE_H, INDOOR_REIHEN)
    reihen(2, OUTDOOR_Y, HALLE_H, OUTDOOR_REIHEN)
    return plaetze


PLAETZE = erzeuge_plaetze()

# Feste Räume im Indoor-Bereich (nur Deko, nicht anklickbar): Name -> (x, y, Breite, Höhe)
RAEUME = {
    "Rezeption & Verleih": (RAND + 20, INDOOR_Y, 28, SERVICE_H),
    "Umkleide": (RAND + 48, INDOOR_Y, 40, SERVICE_H),
    "WC": (RAND + 88, INDOOR_Y, 28, SERVICE_H),
}

# Eingang: Tür in der oberen Wand (von x bis x + Breite)
EINGANG_X, EINGANG_B = RAND + 7, 6

# ---------------------------------------------------------------------------
# 2) Grundriss als SVG zeichnen
# ---------------------------------------------------------------------------
def zeichne_plan(status, gewaehlt):
    """status: {platzname: True/False (verfügbar)}"""
    t = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {PLAN_B} {PLAN_H}" font-family="sans-serif">']
    t.append(f'<rect width="{PLAN_B}" height="{PLAN_H}" fill="white"/>')

    # Indoor-Gebäude (Außenwand)
    t.append(
        f'<rect x="{RAND}" y="{INDOOR_Y}" width="{HALLE_B}" height="{HALLE_H}" '
        f'fill="none" stroke="black" stroke-width="0.6"/>'
    )
    # Outdoor-Fläche (gestrichelter Zaun)
    t.append(
        f'<rect x="{RAND}" y="{OUTDOOR_Y}" width="{HALLE_B}" height="{HALLE_H}" '
        f'fill="#fafafa" stroke="black" stroke-width="0.5" stroke-dasharray="2 1"/>'
    )

    # Eingang: Lücke in der Wand + zwei kleine Striche (Tür)
    x1, x2 = EINGANG_X, EINGANG_X + EINGANG_B
    t.append(f'<line x1="{x1}" y1="{INDOOR_Y}" x2="{x2}" y2="{INDOOR_Y}" stroke="white" stroke-width="1.2"/>')
    t.append(f'<line x1="{x1}" y1="{INDOOR_Y}" x2="{x1}" y2="{INDOOR_Y - 2.5}" stroke="black" stroke-width="0.5"/>')
    t.append(f'<line x1="{x2}" y1="{INDOOR_Y}" x2="{x2}" y2="{INDOOR_Y - 2.5}" stroke="black" stroke-width="0.5"/>')
    t.append(
        f'<text x="{(x1 + x2) / 2}" y="{INDOOR_Y - 3.3}" font-size="2.4" text-anchor="middle" '
        f'fill="black">Eingang</text>'
    )

    # Feste Räume
    for name, (x, y, w, h) in RAEUME.items():
        t.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#f2f2f2" stroke="black" stroke-width="0.4"/>')
        t.append(
            f'<text x="{x + w / 2}" y="{y + h / 2}" font-size="2.4" text-anchor="middle" '
            f'dominant-baseline="middle" fill="black">{escape(name)}</text>'
        )

    # Bereichsbeschriftung
    t.append(f'<text x="{RAND + 1.5}" y="{INDOOR_Y + SERVICE_H - 1.5}" font-size="2.4" fill="#555">Indoor</text>')
    t.append(f'<text x="{RAND + 1.5}" y="{OUTDOOR_Y - 1.2}" font-size="2.4" fill="#555">Outdoor</text>')

    # Plätze (jeder Platz ist eine Gruppe <g>, damit er anklickbar ist)
    for name, (x, y, w, h) in PLAETZE.items():
        frei = status[name]
        if name == gewaehlt:
            fuellung, text = "#ff4b4b", "white"
        elif frei:
            fuellung, text = "black", "white"
        else:
            fuellung, text = "#c8c8c8", "#555555"
        klasse = "frei" if frei else "belegt"
        t.append(f'<g class="{klasse}" data-platz="{name}">')
        t.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fuellung}" '
            f'stroke="black" stroke-width="0.4"/>'
        )
        t.append(
            f'<text x="{x + w / 2}" y="{y + h / 2}" font-size="3" text-anchor="middle" '
            f'dominant-baseline="middle" fill="{text}" pointer-events="none">{name}</text>'
        )
        t.append("</g>")

    t.append("</svg>")
    return "".join(t)


# ---------------------------------------------------------------------------
# Klickbarer Plan: kleine Streamlit-Komponente (nur HTML + JavaScript, kein Zusatzpaket)
# ---------------------------------------------------------------------------
PLAN_HTML = """<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  html, body { margin: 0; padding: 0; background: white; }
  svg { width: 100%; height: auto; display: block; }
  g.frei { cursor: pointer; }
  g.frei:hover rect { stroke: #ff4b4b; stroke-width: 1; }
  g.belegt { cursor: not-allowed; }
</style></head>
<body><div id="root"></div>
<script>
  function senden(typ, daten) {
    window.parent.postMessage(Object.assign({isStreamlitMessage: true, type: typ}, daten), "*");
  }
  function hoeheSetzen() {
    senden("streamlit:setFrameHeight", {height: document.getElementById("root").offsetHeight});
  }
  window.addEventListener("message", function (event) {
    if (event.data.type !== "streamlit:render") return;
    var root = document.getElementById("root");
    root.innerHTML = event.data.args.svg;
    root.querySelectorAll("g.frei").forEach(function (g) {
      g.addEventListener("click", function () {
        senden("streamlit:setComponentValue",
               {value: {platz: g.dataset.platz, n: Date.now()}, dataType: "json"});
      });
    });
    hoeheSetzen();
  });
  window.addEventListener("resize", hoeheSetzen);
  senden("streamlit:componentReady", {apiVersion: 1});
</script></body></html>"""

_komponenten_ordner = Path(tempfile.gettempdir()) / "platzplan_komponente"
_komponenten_ordner.mkdir(exist_ok=True)
(_komponenten_ordner / "index.html").write_text(PLAN_HTML, encoding="utf-8")
platzplan = components.declare_component("platzplan", path=str(_komponenten_ordner))


# ---------------------------------------------------------------------------
# 3) Streamlit-Oberfläche für Schritt 2
# ---------------------------------------------------------------------------
def zeige_schritt2():
    st.subheader("Schritt 2: Platz wählen")

    datum = st.session_state.datum
    start = st.session_state.start
    ende = st.session_state.ende

    st.write(f"**{datum.strftime('%d.%m.%Y')}**, {start.strftime('%H:%M')} – {ende.strftime('%H:%M')} Uhr")

    # --- Verfügbarkeit berechnen -------------------------------------------
    reservierungen = lade_reservierungen()
    status = {name: ist_verfuegbar(name, datum, start, ende, reservierungen) for name in PLAETZE}

    if "gewaehlter_platz" not in st.session_state:
        st.session_state.gewaehlter_platz = None
    # Falls der gewählte Platz durch geänderte Zeit nicht mehr frei ist -> Auswahl zurücksetzen
    if st.session_state.gewaehlter_platz and not status[st.session_state.gewaehlter_platz]:
        st.session_state.gewaehlter_platz = None

    # --- Plan anzeigen (anklickbar) ----------------------------------------
    klick = platzplan(svg=zeichne_plan(status, st.session_state.gewaehlter_platz), key="platzplan", default=None)
    if klick and klick["n"] != st.session_state.get("letzter_klick"):
        st.session_state.letzter_klick = klick["n"]  # jeden Klick nur einmal verarbeiten
        if status.get(klick["platz"]):
            st.session_state.gewaehlter_platz = klick["platz"]
            st.rerun()
    st.caption("Platz im Plan anklicken oder unten per Button wählen · Schwarz = verfügbar · Grau = nicht verfügbar · Rot = gewählt")

    # --- Platz per Button wählen (in der Anordnung des Plans) ---------------
    st.write("**Platz auswählen**")

    def platz_button(name, spalte):
        gewaehlt = st.session_state.gewaehlter_platz == name
        if spalte.button(
            name,
            key=f"btn_{name}",
            disabled=not status[name],
            type="primary" if gewaehlt else "secondary",
            width="stretch",
        ):
            st.session_state.gewaehlter_platz = name
            st.rerun()

    for titel, prefix in (("Indoor", "Platz 1"), ("Outdoor", "Platz 2")):
        st.write(titel)
        namen = [n for n in PLAETZE if n.startswith(prefix)]
        for i in range(0, len(namen), SPALTEN):  # eine Button-Reihe pro Platzreihe im Plan
            reihe = namen[i : i + SPALTEN]
            for spalte, name in zip(st.columns(SPALTEN), reihe):
                platz_button(name, spalte)

    # --- Navigation ---------------------------------------------------------
    st.divider()
    zurueck, weiter = st.columns(2)

    if zurueck.button("← Zurück", width="stretch"):
        st.session_state.schritt = 1
        st.rerun()

    if weiter.button("Weiter →", type="primary", width="stretch"):
        if st.session_state.gewaehlter_platz is None:
            st.warning("Bitte zuerst einen verfügbaren Platz auswählen.")
        else:
            st.session_state.schritt = 3
            st.rerun()