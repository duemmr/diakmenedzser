Magosi Márk Richárd - A5ULPX

# Előszó
A beadandó feladatomban egy primitív diákmenedzser applikációt valósítottam meg azzal a céllal, hogy bemutassam a félév során mennyire tudtam elsajátítani a tanultakat.

# Projekt leírása
A főoldalon lehet hozzáadni tanulókat név és azonosító megadásával, illetve kiválasztható pár előre feltöltött szakból is, hogy mit tanul a hallgató.

Ezen tanulók aztán megjelennek egy táblázatban, ahol név, azonosító, szak, és az összes tantárgy átlaga elérhető róluk.

Jobb egérkattintás bármelyik tanulóra egy menüt hoz elő, amiben két opció van: jegyek megtekintése, tanuló törlése

A jegyek megtekintésére kattintva a "Jegyek szerkesztése" oldal elérhetővé válik, ahol a tanuló szakához társított tantárgyakhoz rendelt jegyek láthatók egy táblázatban, melléjük egy indok és dátum rendelve. Jobb egérkattintás után megjelenő menüvel törölhetők a jegyek is.

# Modulok és függvények
**main.py - Főmodul**

**adatbazis.py - SQLite adatbázis**\
adatbazis_kapcsolodas\
adatbazis_initializalasa_MMR\
diakok_betoltese_MMR\
uj_diak_hozzaadasa_MMR\
diak_torlese_MMR\
jegyek_betoltese_tantargyra_MMR\
uj_jegy_hozzaadasa_MMR\
jegy_torlese_MMR\
atlag_diaknak_MMR\
atlag_diaknak_tantargyra_MMR\
osztalyatlag_tantargyra_MMR\
keres_diak_azonosito_alapjan_MMR

**Diak_MMR.py - Diák osztály**\
adatok_exportalasa_MMR\
adatok_importalasa_MMR

**interface.py - Felhasználói felület**\n
export_adatok\
import_adatok\
letrehoz_menu\
letrehoz_fo_tab\
letrehoz_jegyek_tab\
mutasd_menu\
mutasd_jegy_menu\
mutasd_jegyek_tab\
on_tantargy_kivalaszt\
frissit_jegyek_tablazat\
uj_jegy_hozzadasa\
jegy_torlese\
vissza_a_fooldalra\
frissit_diakok_listaja\
hozzaad_diak\
torol_diak

**tantargyak.py - Konstant, előre feltöltött szakok és tantárgyak**
