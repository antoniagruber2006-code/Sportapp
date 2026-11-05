"""
Sportapp – Platzreservierung

Starten mit:  streamlit run app.py

Ablauf:  Schritt 1 (Datum/Uhrzeit)  ->  Schritt 2 (Platzwahl)  ->  Schritt 3 (Name/E-Mail)
"""

import streamlit as st

from datum import zeige_schritt1
from platzwahl import zeige_schritt2
from name import zeige_bestaetigung, zeige_schritt3

st.set_page_config(page_title="Sportapp", layout="centered")
st.title("Sportapp")

# Aktuellen Schritt merken (1, 2, 3 oder 4 = Bestätigung)
if "schritt" not in st.session_state:
    st.session_state.schritt = 1

# Sicherheit: Man kommt nur zu einem Schritt, wenn die Angaben davor vorhanden sind
if st.session_state.schritt >= 2 and "datum" not in st.session_state:
    st.session_state.schritt = 1
if st.session_state.schritt == 3 and not st.session_state.get("gewaehlter_platz"):
    st.session_state.schritt = 2

schritt = st.session_state.schritt

# Fortschrittsanzeige
TITEL = {1: "Datum und Uhrzeit", 2: "Platzwahl", 3: "Verifikation"}
if schritt in TITEL:
    st.progress(schritt / 3, text=f"Schritt {schritt} von 3: {TITEL[schritt]}")

if schritt == 1:
    zeige_schritt1()
elif schritt == 2:
    zeige_schritt2()
elif schritt == 3:
    zeige_schritt3()
else:
    zeige_bestaetigung()