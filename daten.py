
"""
PlatzPilot – Datenverwaltung
Reservierungen speichern, laden und Verfügbarkeit prüfen.
"""

import csv
from datetime import date, datetime, time, timedelta
from pathlib import Path


# Speicherort und Aufbau der CSV-Datei
DATEI = Path(__file__).parent / "reservierungen.csv"
FELDER = ["platz", "datum", "start", "ende", "name", "email"]

# Mindestabstand zwischen Reservierungen
PUFFER = timedelta(minutes=15)


def lade_reservierungen():
    """Lädt alle Reservierungen aus der CSV-Datei."""
    if not DATEI.exists():
        return []

    reservierungen = []

    with open(DATEI, newline="", encoding="utf-8") as datei:
        for csv_zeile in csv.DictReader(datei):
            reservierungen.append({
                "platz": csv_zeile["platz"],
                "datum": date.fromisoformat(csv_zeile["datum"]),
                "start": time.fromisoformat(csv_zeile["start"]),
                "ende": time.fromisoformat(csv_zeile["ende"]),
                "name": csv_zeile["name"],
                "email": csv_zeile["email"],
            })

    return reservierungen


def speichere_reservierung(platz, datum, start, ende, name, email):
    """Speichert eine neue Reservierung in der CSV-Datei."""
    neue_datei = not DATEI.exists()

    with open(DATEI, "a", newline="", encoding="utf-8") as datei:
        csv_schreiber = csv.DictWriter(datei, fieldnames=FELDER)

        if neue_datei:
            csv_schreiber.writeheader()

        csv_schreiber.writerow({
            "platz": platz,
            "datum": datum.isoformat(),
            "start": start.strftime("%H:%M"),
            "ende": ende.strftime("%H:%M"),
            "name": name,
            "email": email,
        })


def ist_verfuegbar(platz, datum, start, ende, reservierungen=None):
    """Prüft, ob ein Platz inklusive 15-Minuten-Puffer frei ist."""
    if reservierungen is None:
        reservierungen = lade_reservierungen()

    neue_startzeit = datetime.combine(datum, start)
    neue_endzeit = datetime.combine(datum, ende)

    for reservierung in reservierungen:
        # Andere Plätze und Tage überspringen
        if reservierung["platz"] != platz or reservierung["datum"] != datum:
            continue

        # Bestehende Reservierung inklusive Puffer
        bestehende_startzeit = (
            datetime.combine(reservierung["datum"], reservierung["start"])
            - PUFFER
        )
        bestehende_endzeit = (
            datetime.combine(reservierung["datum"], reservierung["ende"])
            + PUFFER
        )

        # Überschneidung der Zeiträume prüfen
        if (
            neue_startzeit < bestehende_endzeit
            and neue_endzeit > bestehende_startzeit
        ):
            return False

    return True
