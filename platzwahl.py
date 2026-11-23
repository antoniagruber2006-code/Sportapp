
"""
PlatzPilot – Schritt 2: Platzwahl

Schwarz = verfügbar
Grau = belegt
Rot = ausgewählt
"""

import tempfile
from html import escape
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from daten import ist_verfuegbar, lade_reservierungen


# ---------------------------------------------------------
# GRUNDRISS
# ---------------------------------------------------------

PLATZ_B, PLATZ_H = 24, 11
RAND = 4

HALLE_B, HALLE_H = 116, 48
INDOOR_Y = 6
OUTDOOR_Y = INDOOR_Y + HALLE_H + 4

PLAN_B = HALLE_B + 2 * RAND
PLAN_H = OUTDOOR_Y + HALLE_H + RAND

SPALTEN = 4
INDOOR_REIHEN = 2
OUTDOOR_REIHEN = 3
SERVICE_H = 14


def erzeuge_plaetze():
    """Erstellt alle Indoor- und Outdoor-Plätze."""
    plaetze = {}

    horizontaler_abstand = (
        HALLE_B - SPALTEN * PLATZ_B
    ) / (SPALTEN + 1)

    def reihen(bereich_nummer, oben, hoehe, anzahl):
        vertikaler_abstand = (
            hoehe - anzahl * PLATZ_H
        ) / (anzahl + 1)

        nummer = 1

        for reihe in range(anzahl):
            for spalte in range(SPALTEN):
                x = (
                    RAND
                    + horizontaler_abstand
                    + spalte * (PLATZ_B + horizontaler_abstand)
                )

                y = (
                    oben
                    + vertikaler_abstand
                    + reihe * (PLATZ_H + vertikaler_abstand)
                )

                name = f"Platz {bereich_nummer}.{nummer:02d}"
                plaetze[name] = (x, y, PLATZ_B, PLATZ_H)
                nummer += 1

    reihen(
        1,
        INDOOR_Y + SERVICE_H,
        HALLE_H - SERVICE_H,
        INDOOR_REIHEN
    )

    reihen(
        2,
        OUTDOOR_Y,
        HALLE_H,
        OUTDOOR_REIHEN
    )

    return plaetze


PLAETZE = erzeuge_plaetze()

RAEUME = {
    "Rezeption & Verleih": (
        RAND + 20, INDOOR_Y, 28, SERVICE_H
    ),
    "Umkleide": (
        RAND + 48, INDOOR_Y, 40, SERVICE_H
    ),
    "WC": (
        RAND + 88, INDOOR_Y, 28, SERVICE_H
    ),
}

EINGANG_X = RAND + 7
EINGANG_B = 6


# ---------------------------------------------------------
# SVG-PLATZPLAN
# ---------------------------------------------------------

def zeichne_plan(status, gewaehlt):
    """Zeichnet den Platzplan mit den Platzfarben."""

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {PLAN_B} {PLAN_H}" '
        f'font-family="sans-serif">'
    ]

    svg.append(
        f'<rect width="{PLAN_B}" height="{PLAN_H}" '
        f'fill="white"/>'
    )

    # Indoor-Gebäude
    svg.append(
        f'<rect x="{RAND}" y="{INDOOR_Y}" '
        f'width="{HALLE_B}" height="{HALLE_H}" '
        f'fill="none" stroke="black" stroke-width="0.6"/>'
    )

    # Outdoor-Bereich
    svg.append(
        f'<rect x="{RAND}" y="{OUTDOOR_Y}" '
        f'width="{HALLE_B}" height="{HALLE_H}" '
        f'fill="#fafafa" stroke="black" '
        f'stroke-width="0.5" stroke-dasharray="2 1"/>'
    )

    # Eingang
    start = EINGANG_X
    ende = EINGANG_X + EINGANG_B

    svg.append(
        f'<line x1="{start}" y1="{INDOOR_Y}" '
        f'x2="{ende}" y2="{INDOOR_Y}" '
        f'stroke="white" stroke-width="1.2"/>'
    )

    svg.append(
        f'<line x1="{start}" y1="{INDOOR_Y}" '
        f'x2="{start}" y2="{INDOOR_Y - 2.5}" '
        f'stroke="black" stroke-width="0.5"/>'
    )

    svg.append(
        f'<line x1="{ende}" y1="{INDOOR_Y}" '
        f'x2="{ende}" y2="{INDOOR_Y - 2.5}" '
        f'stroke="black" stroke-width="0.5"/>'
    )

    svg.append(
        f'<text x="{(start + ende) / 2}" '
        f'y="{INDOOR_Y - 3.3}" '
        f'font-size="2.4" text-anchor="middle" '
        f'fill="black">Eingang</text>'
    )

    # Räume
    for name, (x, y, breite, hoehe) in RAEUME.items():
        svg.append(
            f'<rect x="{x}" y="{y}" '
            f'width="{breite}" height="{hoehe}" '
            f'fill="#f2f2f2" stroke="black" '
            f'stroke-width="0.4"/>'
        )

        svg.append(
            f'<text x="{x + breite / 2}" '
            f'y="{y + hoehe / 2}" '
            f'font-size="2.4" text-anchor="middle" '
            f'dominant-baseline="middle" fill="black">'
            f'{escape(name)}</text>'
        )

    # Beschriftungen
    svg.append(
        f'<text x="{RAND + 1.5}" '
        f'y="{INDOOR_Y + SERVICE_H - 1.5}" '
        f'font-size="2.4" fill="#555">Indoor</text>'
    )

    svg.append(
        f'<text x="{RAND + 1.5}" '
        f'y="{OUTDOOR_Y - 1.2}" '
        f'font-size="2.4" fill="#555">Outdoor</text>'
    )

    # Plätze
    for name, (x, y, breite, hoehe) in PLAETZE.items():

        frei = status[name]

        if name == gewaehlt:
            farbe = "#ff4b4b"
            textfarbe = "white"
        elif frei:
            farbe = "black"
            textfarbe = "white"
        else:
            farbe = "#c8c8c8"
            textfarbe = "#555555"

        klasse = "frei" if frei else "belegt"

        svg.append(
            f'<g class="{klasse}" '
            f'data-platz="{escape(name, quote=True)}">'
        )

        svg.append(
            f'<rect x="{x}" y="{y}" '
            f'width="{breite}" height="{hoehe}" '
            f'fill="{farbe}" stroke="black" '
            f'stroke-width="0.4"/>'
        )

        svg.append(
            f'<text x="{x + breite / 2}" '
            f'y="{y + hoehe / 2}" '
            f'font-size="3" text-anchor="middle" '
            f'dominant-baseline="middle" '
            f'fill="{textfarbe}" pointer-events="none">'
            f'{escape(name)}</text>'
        )

        svg.append("</g>")

    svg.append("</svg>")

    return "".join(svg)


# ---------------------------------------------------------
# KLICKBARER PLATZPLAN
# ---------------------------------------------------------

PLAN_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">

<style>
html, body {
    margin: 0;
    padding: 0;
    background: white;
}

svg {
    width: 100%;
    height: auto;
    display: block;
}

g.frei {
    cursor: pointer;
}

g.frei:hover rect {
    stroke: #ff4b4b;
    stroke-width: 1;
}

g.belegt {
    cursor: not-allowed;
}
</style>
</head>

<body>
<div id="root"></div>

<script>
function senden(typ, daten) {
    window.parent.postMessage(
        Object.assign(
            {isStreamlitMessage: true, type: typ},
            daten
        ),
        "*"
    );
}

function hoeheSetzen() {
    senden("streamlit:setFrameHeight", {
        height: document.getElementById("root").offsetHeight
    });
}

window.addEventListener("message", function(event) {

    if (event.data.type !== "streamlit:render") return;

    var root = document.getElementById("root");
    root.innerHTML = event.data.args.svg;

    root.querySelectorAll("g.frei").forEach(function(g) {
        g.addEventListener("click", function() {
            senden("streamlit:setComponentValue", {
                value: {
                    platz: g.dataset.platz,
                    n: Date.now()
                },
                dataType: "json"
            });
        });
    });

    hoeheSetzen();
});

window.addEventListener("resize", hoeheSetzen);

senden("streamlit:componentReady", {apiVersion: 1});
</script>

</body>
</html>
"""

komponenten_ordner = (
    Path(tempfile.gettempdir()) / "platzplan_komponente"
)

komponenten_ordner.mkdir(
    parents=True,
    exist_ok=True
)

(
    komponenten_ordner / "index.html"
).write_text(
    PLAN_HTML,
    encoding="utf-8"
)

platzplan = components.declare_component(
    "platzplan",
    path=str(komponenten_ordner)
)


# ---------------------------------------------------------
# SCHRITT 2: PLATZWAHL
# ---------------------------------------------------------

def zeige_schritt2():
    """Zeigt ausschließlich den klickbaren Platzplan."""

    st.subheader("Schritt 2: Platz wählen")

    datum = st.session_state.datum
    start = st.session_state.start
    ende = st.session_state.ende

    st.write(
        f"**{datum.strftime('%d.%m.%Y')}**, "
        f"{start.strftime('%H:%M')} – "
        f"{ende.strftime('%H:%M')} Uhr"
    )

    reservierungen = lade_reservierungen()

    platz_status = {
        name: ist_verfuegbar(
            name,
            datum,
            start,
            ende,
            reservierungen
        )
        for name in PLAETZE
    }

    if "gewaehlter_platz" not in st.session_state:
        st.session_state.gewaehlter_platz = None

    gewaehlt = st.session_state.gewaehlter_platz

    if gewaehlt and not platz_status.get(gewaehlt, False):
        st.session_state.gewaehlter_platz = None

    # Nur der klickbare Platzplan
    platz_klick = platzplan(
        svg=zeichne_plan(
            platz_status,
            st.session_state.gewaehlter_platz
        ),
        key="platzplan",
        default=None
    )

    if (
        isinstance(platz_klick, dict)
        and platz_klick.get("n")
        != st.session_state.get("letzter_klick")
    ):
        st.session_state.letzter_klick = platz_klick["n"]

        platz_name = platz_klick.get("platz")

        if platz_status.get(platz_name, False):
            st.session_state.gewaehlter_platz = platz_name
            st.rerun()

    st.caption(
        "Platz direkt im Plan anklicken · "
        "Schwarz = verfügbar · "
        "Grau = belegt · "
        "Rot = ausgewählt"
    )

    if st.session_state.gewaehlter_platz:
        st.success(
            "Ausgewählt: "
            + st.session_state.gewaehlter_platz
        )

    # Navigation
    st.divider()

    zurueck, weiter = st.columns(2)

    if zurueck.button(
        "← Zurück",
        width="stretch"
    ):
        st.session_state.schritt = 1
        st.rerun()

    if weiter.button(
        "Weiter →",
        type="primary",
        width="stretch"
    ):
        if st.session_state.gewaehlter_platz is None:
            st.warning(
                "Bitte zuerst einen verfügbaren Platz auswählen."
            )
        else:
            st.session_state.schritt = 3
            st.rerun()
