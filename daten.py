"""
Gemeinsame Daten-Funktionen für alle Schritte:
Reservierungen in einer CSV-Datei speichern/laden und die Verfügbarkeit prüfen.
"""

import csv
from datetime import date, datetime, time, timedelta
from pathlib import Path

# Die Datei liegt im selben Ordner wie dieses Programm
DATEI = Path(__file__).parent / "reservierungen.csv"
FELDER = ["platz", "datum", "start", "ende", "name", "email"]

# 15 Minuten Abstand zwischen zwei Reservierungen
PUFFER = timedelta(minutes=15)


def lade_reservierungen():
    """Liest alle gespeicherten Reservierungen aus der CSV-Datei."""
    if not DATEI.exists():
        return []

    reservierungen = []
    with open(DATEI, newline="", encoding="utf-8") as datei:
        for zeile in csv.DictReader(datei):
            reservierungen.append({
                "platz": zeile["platz"],
                "datum": date.fromisoformat(zeile["datum"]),
                "start": time.fromisoformat(zeile["start"]),
                "ende": time.fromisoformat(zeile["ende"]),
                "name": zeile["name"],
                "email": zeile["email"],
            })
    return reservierungen


def speichere_reservierung(platz, datum, start, ende, name, email):
    """Hängt eine neue Reservierung an die CSV-Datei an."""
    neue_datei = not DATEI.exists()
    with open(DATEI, "a", newline="", encoding="utf-8") as datei:
        schreiber = csv.DictWriter(datei, fieldnames=FELDER)
        if neue_datei:
            schreiber.writeheader()
        schreiber.writerow({
            "platz": platz,
            "datum": datum.isoformat(),
            "start": start.strftime("%H:%M"),
            "ende": ende.strftime("%H:%M"),
            "name": name,
            "email": email,
        })


def ist_verfuegbar(platz, datum, start, ende, reservierungen=None):
    """True, wenn der Platz im Zeitraum frei ist (inkl. 15 Min. Puffer)."""
    if reservierungen is None:
        reservierungen = lade_reservierungen()

    neu_start = datetime.combine(datum, start)
    neu_ende = datetime.combine(datum, ende)

    for r in reservierungen:
        if r["platz"] != platz or r["datum"] != datum:
            continue
        alt_start = datetime.combine(r["datum"], r["start"]) - PUFFER
        alt_ende = datetime.combine(r["datum"], r["ende"]) + PUFFER
        # Zeiträume überschneiden sich?
        if neu_start < alt_ende and neu_ende > alt_start:
            return False
    return True