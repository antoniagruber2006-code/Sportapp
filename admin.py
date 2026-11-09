import csv
import streamlit as st
from datetime import time

from daten import (
    DATEI,
    FELDER,
    lade_reservierungen,
    ist_verfuegbar,
)

# Dieselbe Platzliste wie auf dem Platzplan verwenden
from platzwahl import PLAETZE


def zeige_admin():
    st.title("Adminbereich")

    reservierungen = lade_reservierungen()

    if not reservierungen:
        st.info("Es gibt noch keine Reservierungen.")
        return

    # Übersicht aller Reservierungen
    st.subheader("Alle Reservierungen")
    st.dataframe(reservierungen, hide_index=True)

    # Reservierung auswählen
    auswahl = st.selectbox(
        "Welche Reservierung möchtest du bearbeiten?",
        range(len(reservierungen)),
        format_func=lambda i: (
            f"{reservierungen[i]['datum'].strftime('%d.%m.%Y')} | "
            f"{reservierungen[i]['platz']} | "
            f"{reservierungen[i]['name']}"
        )
    )

    buchung = reservierungen[auswahl]

    st.subheader("Reservierung ändern")

    # Platz im Dropdown auswählen
    platzliste = list(PLAETZE.keys())

    if buchung["platz"] not in platzliste:
        st.error(
            f"Der gespeicherte Platz '{buchung['platz']}' "
            "ist nicht im aktuellen Platzplan vorhanden. "
            "Bitte wähle einen gültigen Platz aus."
        )
        platz_index = 0
    else:
        platz_index = platzliste.index(buchung["platz"])

    platz = st.selectbox(
        "Platz",
        platzliste,
        index=platz_index
    )

    name = st.text_input(
        "Name",
        value=buchung["name"]
    )

    email = st.text_input(
        "E-Mail",
        value=buchung["email"]
    )

    datum = st.date_input(
        "Datum",
        value=buchung["datum"]
    )

    # Uhrzeiten in 15-Minuten-Schritten
    uhrzeiten = [
        time(stunde, minute)
        for stunde in range(24)
        for minute in [0, 15, 30, 45]
    ]

    start = st.selectbox(
        "Startzeit",
        uhrzeiten,
        index=uhrzeiten.index(buchung["start"]),
        format_func=lambda uhrzeit: uhrzeit.strftime("%H:%M")
    )

    ende = st.selectbox(
        "Endzeit",
        uhrzeiten,
        index=uhrzeiten.index(buchung["ende"]),
        format_func=lambda uhrzeit: uhrzeit.strftime("%H:%M")
    )

    # Änderungen speichern
    if st.button("Änderungen speichern"):

        # Die eigene Buchung bei der Prüfung auslassen
        andere = (
            reservierungen[:auswahl]
            + reservierungen[auswahl + 1:]
        )

        if not name.strip() or not email.strip():
            st.error("Bitte Name und E-Mail ausfüllen.")

        elif ende <= start:
            st.error("Die Endzeit muss nach der Startzeit liegen.")

        elif not ist_verfuegbar(
            platz, datum, start, ende, andere
        ):
            st.error(
                "Der Platz ist belegt oder die 15 Minuten "
                "Abstand werden nicht eingehalten."
            )

        else:
            buchung["platz"] = platz
            buchung["name"] = name.strip()
            buchung["email"] = email.strip()
            buchung["datum"] = datum
            buchung["start"] = start
            buchung["ende"] = ende

            alle_speichern(reservierungen)
            st.success("Die Änderungen wurden gespeichert.")

    # Reservierung löschen
    if st.button("Reservierung löschen"):
        reservierungen.pop(auswahl)
        alle_speichern(reservierungen)
        st.rerun()


def alle_speichern(reservierungen):
    """Speichert die Liste wieder in der CSV-Datei."""

    with open(DATEI, "w", newline="", encoding="utf-8") as datei:
        schreiber = csv.DictWriter(datei, fieldnames=FELDER)
        schreiber.writeheader()

        for buchung in reservierungen:
            schreiber.writerow({
                "platz": buchung["platz"],
                "datum": buchung["datum"].isoformat(),
                "start": buchung["start"].strftime("%H:%M"),
                "ende": buchung["ende"].strftime("%H:%M"),
                "name": buchung["name"],
                "email": buchung["email"],
            })