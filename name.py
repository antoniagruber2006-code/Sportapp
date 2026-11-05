"""
Schritt 3: Verifikation mit Name und E-Mail, danach Bestätigung
"""

import streamlit as st

from daten import ist_verfuegbar, speichere_reservierung


def name_pruefen(name):
    """Gibt einen Fehlertext zurück, oder None wenn der Name passt."""
    teile = name.strip().split()
    # Namen in Wörter aufteilen

    if len(teile) < 2:
        # Vor- oder Nachname fehlt
        return "Bitte Vor- und Nachnamen eingeben!"

    if not all(teil.replace("-", "").isalpha() for teil in teile):
        # Zahlen und Sonderzeichen nicht erlaubt
        return "Bitte einen gültigen Namen eingeben!"

    return None


def email_pruefen(email):
    """Einfache Prüfung der E-Mail-Adresse. Gibt Fehlertext oder None zurück."""
    email = email.strip()
    lokal, _, domain = email.partition("@")

    if (
        email.count("@") != 1
        or " " in email
        or not lokal
        or "." not in domain
        or domain.startswith(".")
        or domain.endswith(".")
    ):
        return "Bitte eine gültige E-Mail-Adresse eingeben!"

    return None


def zeige_schritt3():
    st.subheader("Schritt 3: Verifikation")

    datum = st.session_state.datum
    start = st.session_state.start
    ende = st.session_state.ende
    platz = st.session_state.gewaehlter_platz

    st.write(
        f"**{platz}** am **{datum.strftime('%d.%m.%Y')}** "
        f"von {start.strftime('%H:%M')} bis {ende.strftime('%H:%M')} Uhr"
    )

    name = st.text_input("Vor- und Nachname", value=st.session_state.get("name", ""))
    email = st.text_input("E-Mail-Adresse", value=st.session_state.get("email", ""))

    zurueck, abschliessen = st.columns(2)

    if zurueck.button("← Zurück", width="stretch"):
        st.session_state.name = name
        st.session_state.email = email
        st.session_state.schritt = 2
        st.rerun()

    if abschliessen.button("Reservierung abschließen", type="primary", width="stretch"):
        fehler = name_pruefen(name) or email_pruefen(email)

        if fehler:
            st.error(fehler)
        elif not ist_verfuegbar(platz, datum, start, ende):
            # Falls jemand anderes den Platz in der Zwischenzeit reserviert hat
            st.error("Dieser Platz wurde inzwischen reserviert. Bitte wähle einen anderen Platz.")
        else:
            speichere_reservierung(platz, datum, start, ende, name.strip(), email.strip())
            st.session_state.bestaetigung = {
                "platz": platz,
                "datum": datum,
                "start": start,
                "ende": ende,
                "name": name.strip(),
            }
            st.session_state.schritt = 4
            st.rerun()


def zeige_bestaetigung():
    b = st.session_state.bestaetigung

    st.success("Reservierung erfolgreich!")
    st.write(
        f"**{b['name']}**, dein Platz ist reserviert:\n\n"
        f"- **{b['platz']}**\n"
        f"- {b['datum'].strftime('%d.%m.%Y')}, "
        f"{b['start'].strftime('%H:%M')} bis {b['ende'].strftime('%H:%M')} Uhr"
    )

    if st.button("Neue Reservierung"):
        # Alle Eingaben zurücksetzen
        for schluessel in ["datum", "start", "ende", "gewaehlter_platz", "name", "email", "bestaetigung"]:
            st.session_state.pop(schluessel, None)
        st.session_state.schritt = 1
        st.rerun()