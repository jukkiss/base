import mysql.connector
import geopy.distance
import random

yhteys = mysql.connector.connect(
         host='127.0.0.1',
         port= 3306,
         database='put databasename here',
         user='put username here',
         password='put database password here',
         autocommit=True
         )


# funktio kursorille, kun halutaan monta riviä
def cursor_many(sql, monikko):
    if monikko == ():
        cursor = yhteys.cursor(dictionary=True)
        cursor.execute(sql)
        result = cursor.fetchall()
    else:
        cursor = yhteys.cursor(dictionary=True)
        cursor.execute(sql, monikko)
        result = cursor.fetchall()
    return result


# funktio kursorille, kun halutaan vain yksi rivi
def cursor_one(sql, monikko):
    if monikko == ():
        cursor = yhteys.cursor(dictionary=True)
        cursor.execute(sql)
        result = cursor.fetchone()
    else:
        cursor = yhteys.cursor(dictionary=True)
        cursor.execute(sql, monikko)
        result = cursor.fetchone()
    return result


# funktio taustatarinaan
def taustatarina():
    tarina = input("\nHaluatko lukea taustatarinan (kyllä/ei)?\n")
    if tarina.lower() == "kyllä":
        print("\nIlmastonmuutoksen tuhot uhkaavat suomen lintuja, ja sinä olet huolestunut lintujen tulevaisuudesta.\n"
              "Olet intohimoinen lintukuvaaja, jolle suomen luonto ja linnut ovat lähellä sydäntä.")
        input()
        print("Saat tietää että on keino pelastaa suomen linnut. Luonnonsuojelujärjestöllä on tärkeä pelasta linnut\n"
              "- projekti suunnitteilla, mutta heiltä puuttuu vielä 5000€, jotta projekti voi alkaa. Sinun täytyy kerätä\n"
              "tarvittavat rahat luonnonsuojeluun ja pelastaa hädässä olevat linnut!")
        input()
        print("Mutta millä keinolla saat kerättyä rahat kasaan?")
        input()
        print("Saat idean, että voit lähteä seikkailulle valokuvaamaan lintuja. Tahdot tuoda näkyvyyttä lintujen ja\n"
              "luonnon huononevasta tilanteesta, joten alat myymään valokuvia linnuista kerätäksesi rahat kasaan!")
        input()
        print("Muistat myös että harvinaisemmat linnut ovat arvokkaampia valokuvissa. Joten olet valmis ottamaan riskejä\n"
              "matkustaessasi eri alueille saadaksesi rahat!")
        input()
        print("Suomen luonto ja linnut ansaitsevat pelastuksen, oletko valmis tarttumaan haasteeseen?\n")
        input()

    else:
        print("Olet lintukuvaaja, tehtäväsi on kerätä 5000€ kuvaamalla lintuja.")
        input()


# funktio joka hakee nykyisen pelaajan id:n tietokannasta
def hae_pelaaja_id():
    sql = "SELECT MAX(pelaaja_id) as pelaaja_id FROM pelaaja;"
    result = cursor_one(sql, ())
    return result['pelaaja_id']


# funktio joka hakee pelaajan nykyisen budjetin tietokannasta
def hae_pelaaja_budjetti():
    monikko = (hae_pelaaja_id(),)
    sql = "SELECT budjetti FROM pelaaja WHERE pelaaja_id = %s;"
    result = cursor_one(sql, monikko)
    return result['budjetti']


# funktio joka hakee pelaajan nykyisen kameran id:n ja uuden kameran hinnan tietokannasta
def hae_kameran_id_ja_hinta():
    monikko = ()
    sql = "SELECT kamera_id, hinta FROM kamera;"
    result = cursor_many(sql, monikko)

    monikko = (hae_pelaaja_id(), )
    sql = "SELECT kamera FROM pelaaja WHERE pelaaja_id = %s;"
    pelaajan_kamera = cursor_one(sql, monikko)

    uusi_hinta = 0
    for rivi in result:
        if pelaajan_kamera['kamera'] + 1 == rivi['kamera_id']:
            uusi_hinta = rivi['hinta']

    return pelaajan_kamera['kamera'], uusi_hinta


# funktio joka hakee pelaajan kameran arvo-kertoimen tietokannasta
def hae_pelaajan_kamera():
    monikko = (hae_pelaaja_id(), )
    sql = """SELECT kerroin FROM kamera, pelaaja
    WHERE kamera.kamera_id = pelaaja.kamera AND pelaaja_id = %s;"""
    result = cursor_one(sql, monikko)
    return result['kerroin']


# funktio joka päivittää pelaajan budjetin tietokantaan lintubongailun jälkeen
def uusi_budjetti(arvo):
    budjetti = hae_pelaaja_budjetti() + arvo
    monikko = (budjetti, hae_pelaaja_id())
    sql = "UPDATE pelaaja SET budjetti = %s WHERE pelaaja_id = %s;"
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql, monikko)


# funktio uuden pelaajan luomiseen ja tallentamiseen tietokantaan
def pelaajan_luonti():
    pelaajan_nimi = input("Mikä on nimesi:\n")
    monikko = (pelaajan_nimi, )
    sql = """INSERT INTO pelaaja (pelaajan_nimi, budjetti, kamera, pelaajan_sijainti)
    VALUES (%s, 1000, 1, "EFHK");"""

    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql, monikko)


# funktio pelaajan sijainnin ja budjetin kertomiseen
def pelaajan_sijainti_ja_budjetti():
    monikko = (hae_pelaaja_id(), )
    sql = """SELECT municipality, budjetti 
    FROM airport, pelaaja
    WHERE pelaaja.pelaajan_sijainti = airport.ident AND pelaaja_id = %s"""

    result = cursor_one(sql, monikko)
    print(f"Nykyinen sijaintisi on {result['municipality']} ja budjettisi on {result['budjetti']}€.")


# funktio palauttaa koordinatit pelaajan sijainnista
def pelaajan_koordinatit():
    monikko = (hae_pelaaja_id(),)
    sql = """SELECT latitude_deg, longitude_deg FROM airport, pelaaja
    WHERE airport.ident = pelaaja.pelaajan_sijainti 
    AND pelaaja_id = %s;"""

    result = cursor_one(sql, monikko)
    koordinaatit = (result['latitude_deg'], result['longitude_deg'])
    return koordinaatit


# funktio joka laskee ja tulostaa mihin pelaaja voi matkustaa
def matkustus_vaihtoehdot():
    sql = """SELECT latitude_deg, longitude_deg, municipality, ident FROM airport
    WHERE iso_country = "FI" AND (TYPE = "large_airport" OR TYPE = "medium_airport")
    AND municipality <> '';"""
    result = cursor_many(sql, ())

    print("Voit matkustaa seuraviin kohteisiin:")
    koordinaatit_1 = pelaajan_koordinatit()
    matkustus_vaihtoehdot = []
    for rivi in result:
        koordinaatit_2 = (rivi['latitude_deg'], rivi['longitude_deg'])
        etaisyys = geopy.distance.distance(koordinaatit_1, koordinaatit_2).km

        budjetti = hae_pelaaja_budjetti()
        if etaisyys <= budjetti / 2 and etaisyys != 0:
            print(f"{rivi['municipality']} ({rivi['ident']}), hinta: {etaisyys*2:.0f}€.")
            rivi['hinta'] = etaisyys*2
            matkustus_vaihtoehdot.append(rivi['ident'])
    return result, matkustus_vaihtoehdot


# funktio pelaajan seuraavan kohteen valitsemiseen
def pelaajan_uusi_sijainti(vaihtoehdot):
    uusi_sijainti = input("\nMihin haluat matkustaa?\n")
    while uusi_sijainti.upper() not in vaihtoehdot:
        print("\nSyöttämäsi sijainti ei ole vaihtoehdoissa.")
        uusi_sijainti = input("Syötä oikea sijainti:\n")
    return uusi_sijainti.upper()


# funktio joka päivittää pelaajan sijainnin ja budjetin tietokantaan matkustamisen jälkeen
def paivita_pelaajan_sijainti_ja_budjetti(suomen_kohteet, vaihtoehdot):
    sijainti = pelaajan_uusi_sijainti(vaihtoehdot)
    for rivi in suomen_kohteet:
        if rivi['ident'] == sijainti:
            budjetti = hae_pelaaja_budjetti() - round(rivi['hinta'])
            kaupunki = rivi['municipality']

    sql = """UPDATE pelaaja SET pelaajan_sijainti = %s, budjetti = %s
    WHERE pelaaja_id = %s;"""
    monikko = (sijainti, budjetti, hae_pelaaja_id())
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql, monikko)
    print(f"\nSaavuit paikkaan {kaupunki} ja budjettisi on {budjetti}€.")
    return sijainti


# funktio joka kysyy pelaajalta maaston, ja palauttaa linnut jotka ovat siinä maastossa
def linnun_maasto():
    maasto = input("Mihin maastoon haluat mennä (metsä / vesistö / pelto)?\n")
    while maasto.lower() != "metsä" and maasto.lower() != "vesistö" and maasto.lower() != "pelto":
        print("\nEt valinnut olemassa olevaa maastoa.")
        maasto = input("Mihin maastoon haluat mennä (metsä / vesistö / pelto)?\n")

    monikko = (maasto, )
    sql = """SELECT linnut.lintu_id FROM linnut, maastoliitos, maasto
    WHERE linnut.lintu_id = maastoliitos.lintu_id
    AND maastoliitos.maasto_id = maasto.maasto_id 
    AND maasto_tyyppi = %s;"""
    result = cursor_many(sql, monikko)

    linnut = []
    for rivi in result:
        linnut.append(rivi['lintu_id'])
    return linnut


# funktio joka arpoo linnun lintubongaamiseen ja palauttaa linnun arvon
def linnun_satunnainen_valinta(linnut):
    sql = """SELECT lintu_id, linnun_nimi, arvo, todennäköiysyys FROM linnut;"""
    result = cursor_many(sql, ())
    kaikki_linnut = 0
    for rivi in result:
        if rivi['lintu_id'] in linnut:
            kaikki_linnut = kaikki_linnut + rivi['todennäköiysyys'] * 10
        else:
            kaikki_linnut = kaikki_linnut + rivi['todennäköiysyys']

    random_lintu = random.randint(1, kaikki_linnut)
    n = 0
    while random_lintu > 0:
        lintu = result[n]
        if lintu['lintu_id'] in linnut:
            random_lintu = random_lintu - lintu['todennäköiysyys'] * 10
        else:
            random_lintu = random_lintu - lintu['todennäköiysyys']
        n = n + 1

    kerroin = hae_pelaajan_kamera()
    arvo = 0
    for rivi in result:
        if n == rivi['lintu_id']:
            arvo = rivi['arvo'] * kerroin
            lintu_id = rivi['lintu_id']
            print(f"\nLintu jonka bongasit on {rivi['linnun_nimi']} ja sen kuvan arvo on {arvo}€.")
    return arvo, lintu_id


# funktio joka kysyy pelajaalta jos hän haluaa päivittää kameran ja tarvittaessa päivittää kameran tietokantaan
def kameran_paivittaminen():
    kamera_id, kamera_hinta = hae_kameran_id_ja_hinta()
    if kamera_id != 3 and kamera_hinta < hae_pelaaja_budjetti():
        kameran_paivitys = input(f"Haluatko päivittää kameran (kyllä/ei)? Parempi kamera maksaa {kamera_hinta}€.\n")
        if kameran_paivitys.lower() == "kyllä":
            kamera_id = kamera_id + 1
            monikko = (kamera_id, hae_pelaaja_id())
            sql = "UPDATE pelaaja SET kamera = %s WHERE pelaaja_id = %s;"
            cursor = yhteys.cursor(dictionary=True)
            cursor.execute(sql, monikko)

            uusi_budjetti(- kamera_hinta)
            budjetti = hae_pelaaja_budjetti()
            print(f"\nKameran oston jälkeen, uusi budjettisi on {budjetti}€.")
            input()
        else:
            print()


# funktio joka palauttaa montako kertaa pelaaja on käynyt tietyssä sijainnissa
def onko_pelaaja_ollut_sijainnilla(sijainti):
    monikko = (hae_pelaaja_id(), )
    sql = "SELECT linnun_sijainti, vierailujen_lkm FROM lintujen_sijainnit WHERE pelaaja_id = %s;"
    result = cursor_many(sql, monikko)
    vierailujen_lkm = 0
    for rivi in result:
        if rivi['linnun_sijainti'] == sijainti:
            vierailujen_lkm = rivi['vierailujen_lkm']
    return vierailujen_lkm

# funktio joka luo uuden sijainnin lintujen_sijainnit-tauluun
def luo_uusi_lintu_sijainti(sijainti, lintu_id):
    monikko = (1, "", hae_pelaaja_id(), lintu_id , sijainti)
    sql = """INSERT INTO lintujen_sijainnit 
    (vierailujen_lkm, edellinen_sijainti, pelaaja_id, lintu_id, linnun_sijainti)
    VALUES (%s, %s, %s, %s, %s);"""
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql, monikko)

# funktio joka päivittää sijaintien lukumäärä lintu_sijainnit-tauluun
def paivita_lintu_sijainti(sijainti, vierailujen_lkm, lintu_id):
    uusi_vierailujen_lkm = vierailujen_lkm + 1
    monikko = (uusi_vierailujen_lkm, lintu_id, hae_pelaaja_id(), sijainti)
    sql = """UPDATE lintujen_sijainnit
    SET vierailujen_lkm = %s, lintu_id = %s
    WHERE pelaaja_id = %s AND linnun_sijainti = %s;"""
    cursor = yhteys.cursor(dictionary=True)
    cursor.execute(sql, monikko)


#pääohjelma

print("\nTervetuloa lintupeliin!\n")
pelaajan_luonti()
taustatarina()

vaihtoehdot = ["ei tyhjä"]
x = 1
while hae_pelaaja_budjetti() < 5000 and x == 1:
    pelaajan_sijainti_ja_budjetti()
    input()
    kameran_paivittaminen()
    suomen_kohteet, vaihtoehdot = matkustus_vaihtoehdot()
    if vaihtoehdot != []:
        sijainti = paivita_pelaajan_sijainti_ja_budjetti(suomen_kohteet, vaihtoehdot)
        input()
        vierailujen_lkm = onko_pelaaja_ollut_sijainnilla(sijainti)
        if vierailujen_lkm == 0:
            linnut_maastossa = linnun_maasto()
            linnun_arvo, linnun_id = linnun_satunnainen_valinta(linnut_maastossa)
            input()
            uusi_budjetti(linnun_arvo)
            luo_uusi_lintu_sijainti(sijainti, linnun_id)
        elif vierailujen_lkm < 1:
            linnut_maastossa = linnun_maasto()
            linnun_arvo, linnun_id = linnun_satunnainen_valinta(linnut_maastossa)
            input()
            uusi_budjetti(linnun_arvo)
            paivita_lintu_sijainti(sijainti, vierailujen_lkm, linnun_id)
        else:
            print("Olet käynyt täällä liian monta kertaa. Kohteesta ei enää löydy lintuja.")
            input()
    else:
        x = 0

if hae_pelaaja_budjetti() >= 5000:
    print("\nOnneksi olkoon, olet kerännyt 5000€ luonnonsuojeluun. Linnut on pelastettu!\n"
          "Olet voittanut pelin!")
else:
    print("\nRahat loppuivat, et voi enää matkustaa mihinkään. Olet hävinnyt pelin.")
