import csv

def adatok_exportalasa_MMR(data, fajlnev):
    if not data:
        print("Nincs adat az exportáláshoz.")
        return False
        
    try:
        fejlec = data[0].keys()
        
        with open(fajlnev, mode='w', encoding='utf-8', newline='') as csvfile:
            iro = csv.DictWriter(csvfile, fieldnames=fejlec)
            iro.writeheader()
            iro.writerows(data)

        return True
    except (IOError, IndexError) as e:
        print(f"Exportálási hiba: {e}")

        return False

def adatok_importalasa_MMR(fajlnev):
    try:
        with open(fajlnev, mode='r', encoding='utf-8', newline='') as csvfile:
            olvaso = csv.DictReader(csvfile)
            adatok = list(olvaso)

            return adatok
    except (IOError, FileNotFoundError):
        print(f"Importálási hiba: A fájl nem található vagy olvashatatlan.")
        return None