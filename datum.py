"""
Schritt 1: Datum und Uhrzeit auswählen
"""

from datetime import date, time

import streamlit as st

# Uhrzeiten als Vorschläge erstellen (alle 15 Minuten)
uhrzeiten = []

for stunde in range(24):
    for minute in [0, 15, 30, 45]:
        uhrzeiten.append(time(stunde, minute))


def zeige_schritt1():
    st.subheader("Schritt 1: Datum und Uhrzeit")
    st.write("Wähle das Datum und die Uhrzeit für deine Reservierung.")

    # Bereits gewählte Werte merken (falls man von Schritt 2 zurückkommt)
    gemerktes_datum = max(st.session_state.get("datum", date.today()), date.today())
    gemerkte_start = st.session_state.get("start", time(8, 0))
    gemerkte_ende = st.session_state.get("ende", time(9, 0))

    # Datum auswählen
    datum = st.date_input(
        "Datum auswählen",
        value=gemerktes_datum,
        min_value=date.today()
    )

    # Dropdown-Menü für die Startzeit
    startzeit = st.selectbox(
        "Startzeit auswählen",
        uhrzeiten,
        index=uhrzeiten.index(gemerkte_start),  # 08:00 Uhr ist vorausgewählt
        format_func=lambda uhrzeit: uhrzeit.strftime("%H:%M")
    )

    # Dropdown-Menü für die Endzeit
    endzeit = st.selectbox(
        "Endzeit auswählen",
        uhrzeiten,
        index=uhrzeiten.index(gemerkte_ende),  # 09:00 Uhr ist vorausgewählt
        format_func=lambda uhrzeit: uhrzeit.strftime("%H:%M")
    )

    # Eingaben überprüfen und weiter zu Schritt 2
    if st.button("Weiter zur Platzwahl", type="primary"):
        if endzeit <= startzeit:
            st.error("Die Endzeit muss nach der Startzeit liegen.")
        else:
            st.session_state.datum = datum
            st.session_state.start = startzeit
            st.session_state.ende = endzeit
            st.session_state.schritt = 2
            st.rerun()