from dbConn import getConn
from checker import handleInputInteger
from datetime import date, timedelta

def getNiederlassung():
    """ Definition der Funktion getNiederlassung
    Die Funktion ruft alle Niederlassungen aus der Tabelle Niederlassung ab und gibt sie tabellarisch aus.
    Der Benutzer wird aufgefordert, eine der Niederlassungsnummern einzugeben.
    
    :return eingabe_nlnr - Niederlassungsnummer, die vom Benutzer eingegeben wurde
    :rtype  int
    """
    
    conn = getConn()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT nlnr, ort from niederlassung')
    except:
        print('Abfrage ist fehlerhaft')
        cursor.close()
        return
    
    print('\nNiederlassungen:')
    liste_nlnr = [0]
    for row in cursor:
        print(row[0], ' - ', row[1])
        liste_nlnr.append(row[0])
    cursor.close()
    conn.close()

    # Absicherung, dass die eingegebene Niederlassungsnummer auch in der Liste der Niederlassungsnummern enthalten ist
    # die Eingabeaufforderung wird so oft wiederholt, bis ein Element aus der Liste der Niederlassungsnummern
    # eingegeben wird. Das erste Element der Liste ist 0. HandleInputInteger() liefert im Falle der fehlenden Eingabe
    # 0 zurück. Damit kann die Eingabe durch "Enter" als Eingabe beendet werden.
    eingabe_nlnr = -1
    while eingabe_nlnr not in liste_nlnr:
        eingabe_nlnr = handleInputInteger('Ort eingeben (Nr)')
    # Ende der Absicherung

    return eingabe_nlnr


def getMitarbeiter(p_nlnr):
    """ Definition der Funktion getMitarbeiter
    Die Funktion ruft alle Mitarbeiter mit der übergebenen Niederlassungsnummer ab und gibt
    sie tabellarisch aus.
    Der Benutzer wird aufgefordert eine Mitarbeiternummer einzugeben.

    .param  p_nlnr - Niederlassungsnummer
    :return eingabe_mitnr - Mitarbeiternummer, die vom Benutzer eingegebn wurde
    :rtype  int
    """

    conn = getConn()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT MitID, MitName from Mitarbeiter where nlnr = ?', (p_nlnr))
    except:
        print('Abfrage ist fehlerhaft')
        cursor.close()
        return

    # Leere Ergebnismenge abfangen
    if cursor.rowcount == 0:
        print('Kein Mitarbeiter in der Niederlassung beschäftigt')
        cursor.close()
        return 0

    print('\nMitarbeiter:')
    liste_mit = [0]
    for row in cursor:
        print(row[0], ' - ', row[1])
        liste_mit.append(int(row[0]))
                         
    cursor.close()
    conn.close()

    # Absicherung, dass die eingegebene Mitarbeiternummer einem Mitarbeiter aus der Niederlassung entspricht
    # die Eingabeaufforderung wird so oft wiederholt, bis ein Element aus der Liste der Mitarbeiternummern
    # eingegeben wird. Das erste Element der Liste ist 0. HandleInputInteger() liefert im Falle der fehlenden Eingabe
    # 0 zurück. Damit kann die Eingabe durch "Enter" als Eingabe beendet werden.
    eingabe_mitnr = -1
    while eingabe_mitnr not in liste_mit:
        eingabe_mitnr = handleInputInteger('Mitarbeiternummer eingeben')
    # Ende der Absicherung
    return eingabe_mitnr



from dbConn import getConn
from datetime import date, timedelta

def getAuftrag(p_mitnr):
    """
    6.1 Mitarbeiter-Details anzeigen
    6.2 Aufträge der kommenden Kalenderwoche (Mo-So) anzeigen (sortiert nach ErlDat) inkl. Kundendaten
    """

    conn = getConn()
    cursor = conn.cursor()

    # -------------------------
    # 6.1 Mitarbeiter-Details
    # -------------------------
    try:
        cursor.execute("""
            SELECT MitID, MitName, MitVorname, MitJob, MitStundensatz
            FROM Mitarbeiter
            WHERE MitID = ?
        """, (p_mitnr,))
    except Exception as e:
        print("Abfrage ist fehlerhaft (Mitarbeiter-Details).")
        print("Fehlerdetails:", e)
        cursor.close()
        conn.close()
        return

    mit_row = cursor.fetchone()
    if mit_row is None:
        print("Mitarbeiter nicht gefunden.")
        cursor.close()
        conn.close()
        return

    print("Mitarbeiter-Details:")
    print(f"  MitID:          {mit_row[0]}")
    print(f"  MitName:        {mit_row[1]}")
    print(f"  MitVorname:     {mit_row[2]}")
    print(f"  MitJob:         {mit_row[3]}")
    print(f"  MitStundensatz: {mit_row[4]}")
    print()

    # ---------------------------------------
    # 6.2 Datumsbereich "kommende KW" (Mo-So)
    # ---------------------------------------
    today = date.today()
    monday_this_week = today - timedelta(days=today.weekday())
    monday_next_week = monday_this_week + timedelta(days=7)
    monday_week_after = monday_next_week + timedelta(days=7)

    # -------------------------
    # 6.2 Aufträge + Kunde
    # -------------------------
    try:
        cursor.execute("""
            SELECT
                a.Aufnr,
                a.ErlDat,
                a.Beschreibung,
                k.KunNr,
                k.KunName,
                k.KunOrt,
                k.KunPlz,
                k.KunStrasse
            FROM Auftrag a
            JOIN Kunde k ON k.KunNr = a.KunNr
            WHERE a.MitID = ?
              AND a.ErlDat >= ?
              AND a.ErlDat < ?
            ORDER BY a.ErlDat
        """, (p_mitnr, monday_next_week, monday_week_after))
    except Exception as e:
        print("Abfrage ist fehlerhaft (Aufträge nächste KW).")
        print("Fehlerdetails:", e)
        cursor.close()
        conn.close()
        return

    rows = cursor.fetchall()

    if len(rows) == 0:
        print("Hinweis: Der Mitarbeiter hat in der kommenden Woche keine geplanten Aufträge.")
        cursor.close()
        conn.close()
        return

    # Ausgabe
    end_sunday = monday_week_after - timedelta(days=1)
    print(f"Aufträge in der kommenden Kalenderwoche ({monday_next_week:%d.%m.%Y} - {end_sunday:%d.%m.%Y}):")
    print("-" * 120)
    print(f"{'Aufnr':<6} {'ErlDat':<12} {'KunNr':<6} {'Kunde':<20} {'Ort':<15} {'PLZ':<6} {'Strasse':<20} Beschreibung")
    print("-" * 120)

    for r in rows:
        aufnr = r[0]
        erldat = r[1]
        beschr = r[2]
        kunnr = r[3]
        kunname = r[4]
        kunort = r[5]
        kunplz = r[6]
        kunstr = r[7]

        try:
            erldat_str = erldat.strftime("%d.%m.%Y")
        except:
            erldat_str = str(erldat)

        print(f"{aufnr:<6} {erldat_str:<12} {kunnr:<6} {kunname:<20} {kunort:<15} {kunplz:<6} {kunstr:<20} {beschr}")

    cursor.close()
    conn.close()
