#PlatzPilot 

##Was ist das?
PlatzPilot ist eine Sportplatz-Reservierungsapp. Die Nutzer können Datum, Uhrzeit und einen verfügbaren Tennisplatz auswählen und reservieren. Ein Adminbereich ermöglicht die Verwaltung der Reservierungen. 

###Funktionen Benutzer:
- Datum und Uhrzeit auswählen
- Platzauswahl anhand eines Platzplans
- Vor- und Nachname und E-Mail Eingabe
  
###Funktion Admin:
- Reservierungen löschen
- Reservierungen ändern
- Übersicht aller Reservierungen

##Repository klonen:
```bash
git clone https://github.com/antoniagruber2006-code/Sportapp
```

##Installation der Pakete:
```bash
pip install -r requirements.txt
```
##Starten:
```bash
streamlit run app.py
```

##bekannte Einschränkungen:
Die Reservierungen werden lokal in einer CSV-Datei gespeichert. Es gibt keine automatische Synchronisierung zwischen verschiedenen Geräten.
