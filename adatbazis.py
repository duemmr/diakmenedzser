import sqlite3
import csv
from Diak_MMR import Diak_MMR

DB_FILE = "diakmenedzer.db"

def adatbazis_kapcsolodas():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row

    return conn

def adatbazis_initializalasa_MMR():
    conn = adatbazis_kapcsolodas()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS diakok (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nev TEXT NOT NULL,
            azonosito TEXT NOT NULL UNIQUE,
            szak TEXT NOT NULL
        )
    ''')
    
    cursor.execute("PRAGMA table_info(diakok)")
    oszlopok = [column[1] for column in cursor.fetchall()]
    if 'jegyek' in oszlopok:
        try:
            cursor.execute("ALTER TABLE diakok DROP COLUMN jegyek")
            conn.commit()

            print("Régi 'jegyek' oszlop sikeresen eltávolítva a diákok táblából.")
        except sqlite3.OperationalError as e:
            print(f"Migrációs hiba: {e}")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jegyek (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            diak_azonosito TEXT NOT NULL,
            tantargy_nev TEXT NOT NULL,
            jegy INTEGER NOT NULL,
            indoklas TEXT,
            datum TEXT,
            FOREIGN KEY (diak_azonosito) REFERENCES diakok (azonosito)
        )
    ''')

    cursor.execute("PRAGMA table_info(jegyek)")
    jegy_oszlopok = [column[1] for column in cursor.fetchall()]

    if 'indoklas' not in jegy_oszlopok:
        try:
            cursor.execute("ALTER TABLE jegyek ADD COLUMN indoklas TEXT")
            conn.commit()
            print("'indoklas' oszlop sikeresen hozzáadva a jegyek táblához.")
        except sqlite3.OperationalError as e:
            print(f"Migrációs hiba: {e}")
            
    if 'datum' not in jegy_oszlopok:
        try:
            cursor.execute("ALTER TABLE jegyek ADD COLUMN datum TEXT")
            conn.commit()
            print("'datum' oszlop sikeresen hozzáadva a jegyek táblához.")
        except sqlite3.OperationalError as e:
            print(f"Migrációs hiba: {e}")
            
    conn.close()

def diakok_betoltese_MMR():
    diakok = []

    conn = adatbazis_kapcsolodas()
    cursor = conn.cursor()
    cursor.execute("SELECT nev, azonosito, szak FROM diakok ORDER BY nev")
    sorok = cursor.fetchall()
    conn.close()

    for sor in sorok:
        diakok.append(Diak_MMR(sor['nev'], sor['azonosito'], sor['szak']))

    return diakok

def uj_diak_hozzaadasa_MMR(diak: Diak_MMR):
    conn = adatbazis_kapcsolodas()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO diakok (nev, azonosito, szak) VALUES (?, ?, ?)", (diak.nev, diak.azonosito, diak.szak))
    conn.commit()
    conn.close()

def diak_torlese_MMR(azonosito):
    conn = adatbazis_kapcsolodas()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jegyek WHERE diak_azonosito = ?", (azonosito,))
    cursor.execute("DELETE FROM diakok WHERE azonosito = ?", (azonosito,))
    conn.commit()
    conn.close()

def jegyek_betoltese_tantargyra_MMR(azonosito, tantargy_nev):
    conn = adatbazis_kapcsolodas()
    cursor = conn.cursor()
    cursor.execute("SELECT id, jegy, indoklas, datum FROM jegyek WHERE diak_azonosito = ? AND tantargy_nev = ? ORDER BY datum DESC, id DESC", (azonosito, tantargy_nev))
    sorok = cursor.fetchall()
    conn.close()
    
    return [dict(sor) for sor in sorok]

def uj_jegy_hozzaadasa_MMR(azonosito, tantargy_nev, jegy, indoklas, datum):
    conn = adatbazis_kapcsolodas()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO jegyek (diak_azonosito, tantargy_nev, jegy, indoklas, datum) VALUES (?, ?, ?, ?, ?)", (azonosito, tantargy_nev, jegy, indoklas, datum))
    conn.commit()
    conn.close()

def jegy_torlese_MMR(jegy_id):
    conn = adatbazis_kapcsolodas()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jegyek WHERE id = ?", (jegy_id,))
    conn.commit()
    conn.close()

def atlag_diaknak_MMR(azonosito):
    conn = adatbazis_kapcsolodas()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(jegy) as atlag FROM jegyek WHERE diak_azonosito = ?", (azonosito,))
    sor = cursor.fetchone()
    conn.close()

    return sor['atlag'] if sor and sor['atlag'] is not None else "N/A"

def atlag_diaknak_tantargyra_MMR(azonosito, tantargy_nev):
    conn = adatbazis_kapcsolodas()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(jegy) as atlag FROM jegyek WHERE diak_azonosito = ? AND tantargy_nev = ?", (azonosito, tantargy_nev))
    sor = cursor.fetchone()
    conn.close()

    return sor['atlag'] if sor and sor['atlag'] is not None else 0.0

def osztalyatlag_tantargyra_MMR(tantargy_nev):
    conn = adatbazis_kapcsolodas()
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(jegy) as atlag FROM jegyek WHERE tantargy_nev = ?", (tantargy_nev,))
    sor = cursor.fetchone()
    conn.close()

    return sor['atlag'] if sor and sor['atlag'] is not None else 0.0

def keres_diak_azonosito_alapjan_MMR(azonosito):
    conn = adatbazis_kapcsolodas()
    cursor = conn.cursor()
    cursor.execute("SELECT nev, azonosito, szak FROM diakok WHERE azonosito = ?", (azonosito,))
    sor = cursor.fetchone()
    conn.close()

    if sor:
        return Diak_MMR(sor['nev'], sor['azonosito'], sor['szak'])

    return None