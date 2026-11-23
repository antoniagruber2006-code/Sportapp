
import csv
from datetime import time

import streamlit as st

from daten import DATEI, FELDER, lade_reservierungen, ist_verfuegbar
from platzwahl import PLAETZE


def zeige_admin():
    st.title("Adminbereich")

    reservierungen = lade_reservierungen()

    if not reservierungen:
        st.info("Es gibt noch keine Reservierungen.")
        return

    # Alle Reservierungen anzeigen
    st.subheader("Alle Reservierungen")
    st.dataframe(reservierungen, hide_index=True)

    # Reservierung zur Bearbeitung auswählen
    reservierung_index = st.selectbox(
        "Welche Reservierung möchtest du bearbeiten?",
        range(len(reservierungen)),
        format_func=lambda index: (
            f"{reservierungen[index]['datum'].strftime('%d.%m.%Y')} | "
            f"{reservierungen[index]['platz']} | "
            f"{reservierungen[index]['name']}"
        )
    )

    ausgewaehlte_reservierung = reservierungen[reservierung_index]

    st.subheader("Reservierung ändern")

    # Verfügbare Plätze aus dem Platzplan laden
    platzliste = list(PLAETZE.keys())

    if ausgewaehlte_reservierung["platz"] not in platzliste:
        st.error(
            f"Der gespeicherte Platz '{ausgewaehlte_reservierung['platz']}' "
            "ist nicht im aktuellen Platzplan vorhanden. "
            "Bitte wähle einen gültigen Platz aus."
        )
        platz_index = 0
    else:
        platz_index = platzliste.index(ausgewaehlte_reservierung["platz"])

    neuer_platz = st.selectbox(
        "Platz",
        platzliste,
        index=platz_index
    )

    neuer_name = st.text_input(
        "Name",
        value=ausgewaehlte_reservierung["name"]
    )

    neue_email = st.text_input(
        "E-Mail",
        value=ausgewaehlte_reservierung["email"]
    )

    neues_datum = st.date_input(
        "Datum",
        value=ausgewaehlte_reservierung["datum"]
    )

    # Uhrzeiten in 15-Minuten-Schritten
    uhrzeiten = [
        time(stunde, minute)
        for stunde in range(24)
        for minute in (0, 15, 30, 45)
    ]

    neue_startzeit = st.selectbox(
        "Startzeit",
        uhrzeiten,
        index=uhrzeiten.index(ausgewaehlte_reservierung["start"]),
        format_func=lambda uhrzeit: uhrzeit.strftime("%H:%M")
    )

    neue_endzeit = st.selectbox(
        "Endzeit",
        uhrzeiten,
        index=uhrzeiten.index(ausgewaehlte_reservierung["ende"]),
        format_func=lambda uhrzeit: uhrzeit.strftime("%H:%M")
    )

    # Änderungen speichern
    if st.button("Änderungen speichern"):

        # Ausgewählte Reservierung bei der Verfügbarkeitsprüfung ausschließen
        andere_reservierungen = (
            reservierungen[:reservierung_index]
            + reservierungen[reservierung_index + 1:]
        )

        if not neuer_name.strip() or not neue_email.strip():
            st.error("Bitte Name und E-Mail ausfüllen.")

        elif neue_endzeit <= neue_startzeit:
            st.error("Die Endzeit muss nach der Startzeit liegen.")

        elif not ist_verfuegbar(
            neuer_platz,
            neues_datum,
            neue_startzeit,
            neue_endzeit,
            andere_reservierungen
        ):
            st.error(
                "Der Platz ist belegt oder die 15 Minuten "
                "Abstand werden nicht eingehalten."
            )

        else:
            ausgewaehlte_reservierung["platz"] = neuer_platz
            ausgewaehlte_reservierung["name"] = neuer_name.strip()
            ausgewaehlte_reservierung["email"] = neue_email.strip()
            ausgewaehlte_reservierung["datum"] = neues_datum
            ausgewaehlte_reservierung["start"] = neue_startzeit
            ausgewaehlte_reservierung["ende"] = neue_endzeit

            alle_speichern(reservierungen)
            st.success("Die Änderungen wurden gespeichert.")

    # Reservierung löschen
    if st.button("Reservierung löschen"):
        reservierungen.pop(reservierung_index)
        alle_speichern(reservierungen)
        st.rerun()


def alle_speichern(reservierungen):
    """Speichert alle Reservierungen in der CSV-Datei."""

    with open(DATEI, "w", newline="", encoding="utf-8") as datei:
        csv_schreiber = csv.DictWriter(datei, fieldnames=FELDER)
        csv_schreiber.writeheader()

        for reservierung in reservierungen:
            csv_schreiber.writerow({
                "platz": reservierung["platz"],
                "datum": reservierung["datum"].isoformat(),
                "start": reservierung["start"].strftime("%H:%M"),
                "ende": reservierung["ende"].strftime("%H:%M"),
                "name": reservierung["name"],
                "email": reservierung["email"],
            })
