
"""
PlatzPilot – Schritt 3
Name und E-Mail eingeben und Reservierung bestätigen.
"""

import streamlit as st

from daten import ist_verfuegbar, speichere_reservierung


def name_pruefen(name):
    """Prüft den Vor- und Nachnamen."""
    namensbestandteile = name.strip().split()

    if len(namensbestandteile) < 2:
        return "Bitte Vor- und Nachnamen eingeben!"

    if not all(
        bestandteil.replace("-", "").isalpha()
        for bestandteil in namensbestandteile
    ):
        return "Bitte einen gültigen Namen eingeben!"

    return None


def zeige_schritt3():
    """Zeigt die Eingabefelder und schließt die Reservierung ab."""
    st.subheader("Schritt 3: Verifikation")

    reservierungsdatum = st.session_state.datum
    startzeit = st.session_state.start
    endzeit = st.session_state.ende
    ausgewaehlter_platz = st.session_state.gewaehlter_platz

    # Ausgewählte Reservierung anzeigen
    st.write(
        f"**{ausgewaehlter_platz}** am "
        f"**{reservierungsdatum.strftime('%d.%m.%Y')}** "
        f"von {startzeit.strftime('%H:%M')} "
        f"bis {endzeit.strftime('%H:%M')} Uhr"
    )

    # Persönliche Daten eingeben
    name = st.text_input(
        "Vor- und Nachname",
        value=st.session_state.get("name", "")
    )

    email = st.text_input(
        "E-Mail-Adresse",
        value=st.session_state.get("email", "")
    )

    zurueck_spalte, abschliessen_spalte = st.columns(2)

    # Zurück zur Platzwahl
    if zurueck_spalte.button("← Zurück", width="stretch"):
        st.session_state.name = name
        st.session_state.email = email
        st.session_state.schritt = 2
        st.rerun()

    # Reservierung abschließen
    if abschliessen_spalte.button(
        "Reservierung abschließen",
        type="primary",
        width="stretch"
    ):
        fehlermeldung = name_pruefen(name)

        if fehlermeldung:
            st.error(fehlermeldung)

        elif not email.strip():
            st.error("Bitte eine E-Mail-Adresse eingeben!")

        elif not ist_verfuegbar(
            ausgewaehlter_platz,
            reservierungsdatum,
            startzeit,
            endzeit
        ):
            st.error(
                "Dieser Platz wurde inzwischen reserviert. "
                "Bitte wähle einen anderen Platz."
            )

        else:
            speichere_reservierung(
                ausgewaehlter_platz,
                reservierungsdatum,
                startzeit,
                endzeit,
                name.strip(),
                email.strip()
            )

            st.session_state.bestaetigung = {
                "platz": ausgewaehlter_platz,
                "datum": reservierungsdatum,
                "start": startzeit,
                "ende": endzeit,
                "name": name.strip(),
            }

            st.session_state.schritt = 4
            st.rerun()


def zeige_bestaetigung():
    """Zeigt die erfolgreiche Reservierung an."""
    bestaetigte_reservierung = st.session_state.bestaetigung

    st.success("Reservierung erfolgreich!")

    st.write(
        f"**{bestaetigte_reservierung['name']}**, "
        f"dein Platz ist reserviert:\n\n"
        f"- **{bestaetigte_reservierung['platz']}**\n"
        f"- {bestaetigte_reservierung['datum'].strftime('%d.%m.%Y')}, "
        f"{bestaetigte_reservierung['start'].strftime('%H:%M')} "
        f"bis {bestaetigte_reservierung['ende'].strftime('%H:%M')} Uhr"
    )

    # Neue Reservierung beginnen
    if st.button("Neue Reservierung"):
        for schluessel in [
            "datum",
            "start",
            "ende",
            "gewaehlter_platz",
            "name",
            "email",
            "bestaetigung"
        ]:
            st.session_state.pop(schluessel, None)

        st.session_state.schritt = 1
        st.rerun()
