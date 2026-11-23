
"""
PlatzPilot – Platzreservierung
Starten mit: streamlit run app.py
"""

import streamlit as st

from datum import zeige_schritt1
from platzwahl import zeige_schritt2
from name import zeige_bestaetigung, zeige_schritt3
from admin import zeige_admin


# Seiteneinstellungen
st.set_page_config(
    page_title="🎾 PlatzPilot",
    layout="centered"
)


# DESIGN
st.markdown("""
<style>
    /* Streamlit-Menü ausblenden */
    [data-testid="stToolbar"] {
        display: none;
    }

    /* Hintergrund und Textfarbe */
    .stApp {
        background-color: #F2F8F2;
        color: #173B29;
    }

    /* Seitenbreite und Abstände */
    .block-container {
        max-width: 850px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
    }

    /* Überschriften */
    h1 {
        color: #123D28;
        font-weight: 800;
    }

    h2, h3 {
        color: #205C38;
    }

    /* Buttons */
    .stButton > button {
        background-color: #237A46;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
    }

    .stButton > button:hover {
        background-color: #165C33;
        color: white;
    }

    /* Seitenleiste */
    [data-testid="stSidebar"] {
        background-color: #E0F0E2;
    }

    /* Tennis-Banner */
    .tennis-banner {
        position: relative;
        overflow: hidden;
        min-height: 190px;
        border-radius: 20px;
        background: linear-gradient(115deg, #124C30, #278B50);
        margin: 20px 0 30px 0;
        padding: 28px;
        color: white;
    }

    .banner-text {
        position: relative;
        z-index: 2;
        max-width: 55%;
    }

    .banner-text h2 {
        color: white;
        font-size: 27px;
        margin: 0 0 10px 0;
    }

    .banner-text p {
        color: #DBF2DE;
        font-size: 15px;
    }

    /* Tennisplatz */
    .tennisplatz {
        position: absolute;
        right: -20px;
        top: 25px;
        width: 230px;
        height: 140px;
        border: 3px solid rgba(255, 255, 255, 0.8);
        transform: rotate(-12deg);
    }

    .tennisplatz::before {
        content: "";
        position: absolute;
        left: 50%;
        top: 0;
        height: 100%;
        border-left: 3px solid rgba(255, 255, 255, 0.8);
    }

    .tennisplatz::after {
        content: "";
        position: absolute;
        left: 20%;
        right: 20%;
        top: 50%;
        border-top: 2px solid rgba(255, 255, 255, 0.8);
    }

    /* Tennisball */
    .tennisball {
        position: absolute;
        right: 90px;
        top: 60px;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background-color: #D9EE53;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }

    /* Smartphone-Ansicht */
    @media (max-width: 600px) {
        .banner-text {
            max-width: 65%;
        }

        .banner-text h2 {
            font-size: 22px;
        }

        .tennisplatz {
            right: -100px;
        }

        .tennisball {
            right: 25px;
        }
    }
</style>
""", unsafe_allow_html=True)


# ADMIN-ANMELDUNG

# Anmeldestatus speichern
if "admin_angemeldet" not in st.session_state:
    st.session_state.admin_angemeldet = False

# Adminzugang oben rechts
linke_spalte, rechte_spalte = st.columns([3, 1])

with rechte_spalte:
    if not st.session_state.admin_angemeldet:
        with st.popover("Admin anmelden"):
            admin_passwort = st.text_input(
                "Passwort",
                type="password"
            )

            if st.button("Anmelden"):
                if admin_passwort == "platzpilot123":
                    st.session_state.admin_angemeldet = True
                    st.rerun()
                else:
                    st.error("Das Passwort ist falsch.")

    else:
        st.write("Admin angemeldet")

        if st.button("Abmelden"):
            st.session_state.admin_angemeldet = False
            st.rerun()


# Navigation für angemeldete Administratoren
if st.session_state.admin_angemeldet:
    ausgewaehlte_seite = st.sidebar.radio(
        "Bereich auswählen",
        ["Reservierung", "Adminbereich"]
    )
else:
    ausgewaehlte_seite = "Reservierung"


# ADMINBEREICH
if ausgewaehlte_seite == "Adminbereich":
    zeige_admin()


# RESERVIERUNG
else:
    st.title("🎾 PlatzPilot")
    st.write("Dein Platz. Dein Match. Deine Zeit.")

    # Aktuellen Reservierungsschritt speichern
    if "schritt" not in st.session_state:
        st.session_state.schritt = 1

    # Fehlende Datumsangabe prüfen
    if (
        st.session_state.schritt >= 2
        and "datum" not in st.session_state
    ):
        st.session_state.schritt = 1

    # Fehlende Platzauswahl prüfen
    if (
        st.session_state.schritt == 3
        and not st.session_state.get("gewaehlter_platz")
    ):
        st.session_state.schritt = 2

    aktueller_schritt = st.session_state.schritt

    # Tennis-Banner nur beim ersten Schritt anzeigen
    if aktueller_schritt == 1:
        st.markdown(
            """
<div class="tennis-banner">
<div class="banner-text">
<h2>Bereit für dein Match?</h2>
<p>Wähle deine Zeit und sichere dir deinen Platz.</p>
</div>
<div class="tennisplatz"></div>
<div class="tennisball"></div>
</div>
            """,
            unsafe_allow_html=True
        )

    SCHRITT_TITEL = {
        1: "Datum und Uhrzeit",
        2: "Platzwahl",
        3: "Verifikation"
    }

    # Fortschritt der Reservierung anzeigen
    if aktueller_schritt in SCHRITT_TITEL:
        st.progress(
            aktueller_schritt / 3,
            text=(
                f"Schritt {aktueller_schritt} von 3: "
                f"{SCHRITT_TITEL[aktueller_schritt]}"
            )
        )

    # Passende Reservierungsseite öffnen
    if aktueller_schritt == 1:
        zeige_schritt1()

    elif aktueller_schritt == 2:
        zeige_schritt2()

    elif aktueller_schritt == 3:
        zeige_schritt3()

    else:
        zeige_bestaetigung()
