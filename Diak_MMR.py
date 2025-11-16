class Diak_MMR:
    def __init__(self, nev, azonosito, szak):
        self.nev = nev
        self.azonosito = azonosito
        self.szak = szak

    def __str__(self):
        return f"{self.nev} ({self.azonosito}) - {self.szak}"