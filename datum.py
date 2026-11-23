
"""
PlatzPilot – Schritt 1
Datum und Uhrzeit für die Reservierung auswählen.

Reservierungen sind zwischen 07:00 und 23:00 Uhr möglich.
"""

from datetime import date, time
import streamlit as st


# ---------------------------------------------------------
# UHRZEITEN IN 15-MINUTEN-SCHRITTEN
# ---------------------------------------------------------

# Startzeiten von 07:00 bis 22:45 Uhr
startzeiten = [
    time(stunde, minute)
    for stunde in range(7, 23)
    for minute in (0, 15, 30, 45)
]

# Endzeiten von 07:15 bis 23:00 Uhr
endzeiten = [
    time(stunde, minute)
    for stunde in range(7, 23)
    for minute in (0, 15, 30, 45)
    if not (stunde == 7 and minute == 0)
]

# 23:00 Uhr als letzte Endzeit hinzufügen
endzeiten.append(time(23, 0))


# ---------------------------------------------------------
# SCHRITT 1: DATUM UND UHRZEIT
# ---------------------------------------------------------

def zeige_schritt1():
    """Zeigt die Auswahl von Datum, Startzeit und Endzeit."""

    st.subheader("Schritt 1: Datum und Uhrzeit")

    st.write(
        "Wähle das Datum und die Uhrzeit für deine Reservierung."
    )

    st.caption(
        "Reservierungen sind täglich von 07:00 bis 23:00 Uhr möglich."
    )

    # Bereits ausgewählte Werte wiederherstellen
    gespeichertes_datum = max(
        st.session_state.get("datum", date.today()),
        date.today()
    )

    gespeicherte_startzeit = st.session_state.get("start", None)
    gespeicherte_endzeit = st.session_state.get("ende", None)

    # -----------------------------------------------------
    # DATUM AUSWÄHLEN
    # -----------------------------------------------------

    ausgewaehltes_datum = st.date_input(
        "Datum auswählen",
        value=gespeichertes_datum,
        min_value=date.today()
    )

    # -----------------------------------------------------
    # STARTZEIT AUSWÄHLEN
    # -----------------------------------------------------

    startzeit = st.selectbox(
        "Startzeit auswählen",
        startzeiten,
        index=(
            startzeiten.index(gespeicherte_startzeit)
            if gespeicherte_startzeit in startzeiten
            else None
        ),
        placeholder="Bitte Startzeit auswählen",
        format_func=lambda uhrzeit: uhrzeit.strftime("%H:%M")
    )

    # -----------------------------------------------------
    # ENDZEIT AUSWÄHLEN
    # -----------------------------------------------------

    # Nur Endzeiten nach der Startzeit anzeigen
    if startzeit is not None:
        moegliche_endzeiten = [
            uhrzeit
            for uhrzeit in endzeiten
            if uhrzeit > startzeit
        ]
    else:
        moegliche_endzeiten = []

    endzeit = st.selectbox(
        "Endzeit auswählen",
        moegliche_endzeiten,
        index=(
            moegliche_endzeiten.index(gespeicherte_endzeit)
            if gespeicherte_endzeit in moegliche_endzeiten
            else None
        ),
        placeholder="Bitte Endzeit auswählen",
        format_func=lambda uhrzeit: uhrzeit.strftime("%H:%M"),
        disabled=startzeit is None
    )

    # -----------------------------------------------------
    # WEITER ZUR PLATZWAHL
    # -----------------------------------------------------

    if st.button(
        "Weiter zur Platzwahl",
        type="primary"
    ):

        if startzeit is None:
            st.error(
                "Bitte zuerst eine Startzeit auswählen."
            )

        elif endzeit is None:
            st.error(
                "Bitte eine Endzeit auswählen."
            )

        elif endzeit <= startzeit:
            st.error(
                "Die Endzeit muss nach der Startzeit liegen."
            )

        else:
            st.session_state.datum = ausgewaehltes_datum
            st.session_state.start = startzeit
            st.session_state.ende = endzeit

            st.session_state.schritt = 2

            st.rerun()
