import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from datetime import datetime
from tantargyak import TANTARGYAK_SZAKONKENT
from adatkezeles import adatok_exportalasa_MMR, adatok_importalasa_MMR
from adatbazis import (
    Diak_MMR,
    adatbazis_kapcsolodas,
    adatbazis_initializalasa_MMR,
    diakok_betoltese_MMR,
    uj_diak_hozzaadasa_MMR,
    diak_torlese_MMR,
    keres_diak_azonosito_alapjan_MMR,
    jegyek_betoltese_tantargyra_MMR,
    uj_jegy_hozzaadasa_MMR,
    jegy_torlese_MMR,
    atlag_diaknak_MMR,
    atlag_diaknak_tantargyra_MMR,
    osztalyatlag_tantargyra_MMR
)

class Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Diákmenedzser")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        adatbazis_initializalasa_MMR()
        
        self.diakok = diakok_betoltese_MMR()
        self.kivalasztott_diak_obj = None
        self.kivalasztott_tantargy = None

        self.letrehoz_menu()

        self.naplo = ttk.Notebook(self.root)
        self.naplo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.fo_tab_keret = ttk.Frame(self.naplo)
        self.jegyek_tab_keret = ttk.Frame(self.naplo)
        
        self.naplo.add(self.fo_tab_keret, text="Diákok")
        self.naplo.add(self.jegyek_tab_keret, text="Jegyek szerkesztése")
        
        self.letrehoz_fo_tab()
        self.letrehoz_jegyek_tab()
        
        self.naplo.tab(1, state="disabled")
        self.frissit_diakok_listaja()
       
    def export_adatok(self):
        fajlnev = filedialog.asksaveasfilename(title="Adatok mentése másként...", defaultextension=".csv", filetypes=[("CSV fájlok", "*.csv"), ("Minden fájl", "*.*")])
        if not fajlnev:
            return

        conn = adatbazis_kapcsolodas()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.nev, d.azonosito, d.szak, j.tantargy_nev, j.jegy, j.indoklas, j.datum 
            FROM diakok d 
            LEFT JOIN jegyek j ON d.azonosito = j.diak_azonosito 
            ORDER BY d.nev, j.tantargy_nev
        ''')

        adatok = [dict(sor) for sor in cursor.fetchall()] 
        conn.close()

        if adatok_exportalasa_MMR(adatok, fajlnev):
            messagebox.showinfo("Siker", f"Az adatok sikeresen exportálva ide:\n{fajlnev}")
        else:
            messagebox.showerror("Hiba", "Az exportálás sikertelen!")

    def import_adatok(self):
        fajlnev = filedialog.askopenfilename(title="Válassz importálandó fájlt", filetypes=[("CSV fájlok", "*.csv"), ("Minden fájl", "*.*")])
        if not fajlnev:
            return

        importalt_adatok = adatok_importalasa_MMR(fajlnev)

        if importalt_adatok is None:
            messagebox.showerror("Hiba", "A fájl megnyitása sikertelen!")
            return

        importalt_diakok = 0
        importalt_jegyek = 0
        hibas_sorok = 0
        
        conn = adatbazis_kapcsolodas()
        cursor = conn.cursor()
        
        try:
            for sor in importalt_adatok:
                try:
                    nev = sor.get("nev", "")
                    azonosito = sor.get("azonosito", "")
                    szak = sor.get("szak", "")
                    tantargy_nev = sor.get("tantargy_nev", "")
                    jegy_str = sor.get("jegy", "")
                    indoklas = sor.get("indoklas", "")
                    datum = sor.get("datum", "")

                    if azonosito and not keres_diak_azonosito_alapjan_MMR(azonosito):
                        uj_diak = Diak_MMR(nev, azonosito, szak)
                        uj_diak_hozzaadasa_MMR(uj_diak)

                        importalt_diakok += 1

                    if tantargy_nev and jegy_str and jegy_str.isdigit():
                        jegy = int(jegy_str)

                        uj_jegy_hozzaadasa_MMR(azonosito, tantargy_nev, jegy, indoklas, datum)

                        importalt_jegyek += 1
                except (ValueError, IndexError):
                    hibas_sorok += 1
                    continue
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Adatbázis hiba", f"Hiba történt az importálás során: {e}")

            return
        finally:
            conn.close()

        self.diakok = diakok_betoltese_MMR()
        self.frissit_diakok_listaja()

        uzenet = f"Importálás befejeződött\n\n"
        uzenet += f"Új diák hozzáadva: {importalt_diakok}\n"
        uzenet += f"Jegy importálva: {importalt_jegyek}\n"

        if hibas_sorok > 0:
            uzenet += f"Hibás sorok kihagyva: {hibas_sorok}"
        
        messagebox.showinfo("Importálás eredménye", uzenet)

    def letrehoz_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fájl", menu=file_menu)
        file_menu.add_command(label="Importálás fájlból...", command=self.import_adatok)
        file_menu.add_separator()
        file_menu.add_command(label="Exportálás fájlba...", command=self.export_adatok)

    def letrehoz_fo_tab(self):
        input_keret = ttk.LabelFrame(self.fo_tab_keret, text="Új diák hozzáadása", padding="10")
        input_keret.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(input_keret, text="Név:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.nev_entry = ttk.Entry(input_keret, width=30)
        self.nev_entry.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(input_keret, text="Azonosító:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.azonosito_entry = ttk.Entry(input_keret, width=30)
        self.azonosito_entry.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(input_keret, text="Szak:").grid(row=2, column=0, sticky=tk.W, padx=5)
        szakok = list(TANTARGYAK_SZAKONKENT.keys())

        self.szak_combobox = ttk.Combobox(input_keret, values=szakok, width=28, state="readonly")
        self.szak_combobox.grid(row=2, column=1, padx=5, pady=2)
        self.szak_combobox.current(0)

        gomb_keret = ttk.Frame(input_keret)
        gomb_keret.grid(row=3, column=0, columnspan=2, pady=10)
        hozzaad_gomb = ttk.Button(gomb_keret, text="Diák hozzáadása", command=self.hozzaad_diak)
        hozzaad_gomb.pack(side=tk.LEFT, padx=5)

        lista_keret = ttk.LabelFrame(self.fo_tab_keret, text="Diákok listája", padding="10")
        lista_keret.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        self.tree = ttk.Treeview(lista_keret, columns=("Név", "Azonosító", "Szak", "Átlag"), show="headings")
        self.tree.heading("Név", text="Név")
        self.tree.heading("Azonosító", text="Azonosító")
        self.tree.heading("Szak", text="Szak")
        self.tree.heading("Átlag", text="Átlag")
        self.tree.column("Név", width=200)
        self.tree.column("Azonosító", width=100)
        self.tree.column("Szak", width=150)
        self.tree.column("Átlag", width=80, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(lista_keret, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Button-3>", self.mutasd_menu)
        
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Jegyek", command=self.mutasd_jegyek_tab)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Törlés", command=self.torol_diak)

    def letrehoz_jegyek_tab(self):
        main_keret = ttk.Frame(self.jegyek_tab_keret, padding="10")
        main_keret.pack(fill=tk.BOTH, expand=True)

        self.jegyek_cimke = ttk.Label(main_keret, text="", font=("Helvetica", 14, "bold"))
        self.jegyek_cimke.pack(pady=10)

        paned_window = ttk.PanedWindow(main_keret, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        left_keret = ttk.Frame(paned_window)
        paned_window.add(left_keret, weight=1)

        ttk.Label(left_keret, text="Tantárgyak", font=("Helvetica", 12, "bold")).pack(pady=5)
        
        self.tantargy_tree = ttk.Treeview(left_keret, columns=("tantargy", "tanulo_atlag", "osztaly_atlag"), show="headings")
        self.tantargy_tree.heading("tantargy", text="Tantárgy")
        self.tantargy_tree.heading("tanulo_atlag", text="Tanuló átlaga")
        self.tantargy_tree.heading("osztaly_atlag", text="Osztály átlaga")
        self.tantargy_tree.column("tantargy", width=150)
        self.tantargy_tree.column("tanulo_atlag", width=80, anchor=tk.CENTER)
        self.tantargy_tree.column("osztaly_atlag", width=80, anchor=tk.CENTER)
        
        self.tantargy_tree.bind('<<TreeviewSelect>>', self.on_tantargy_kivalaszt)
        self.tantargy_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        right_keret = ttk.Frame(paned_window)
        paned_window.add(right_keret, weight=3)

        ttk.Label(right_keret, text="Jegyek és indoklás", font=("Helvetica", 12, "bold")).pack(pady=5)
        
        table_and_button_container = ttk.Frame(right_keret)
        table_and_button_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.jegyek_tree = ttk.Treeview(table_and_button_container, columns=("jegy", "indoklas", "datum"), show="headings")
        self.jegyek_tree.heading("jegy", text="Jegy")
        self.jegyek_tree.heading("indoklas", text="Indoklás")
        self.jegyek_tree.heading("datum", text="Dátum")
        self.jegyek_tree.column("jegy", width=80, anchor=tk.CENTER)
        self.jegyek_tree.column("indoklas", width=250)
        self.jegyek_tree.column("datum", width=100, anchor=tk.CENTER)
        
        jegy_scrollbar = ttk.Scrollbar(table_and_button_container, orient=tk.VERTICAL, command=self.jegyek_tree.yview)
        self.jegyek_tree.configure(yscroll=jegy_scrollbar.set)
        
        self.jegyek_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        jegy_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.jegyek_tree.bind("<Button-3>", self.mutasd_jegy_menu)
        self.jegy_context_menu = tk.Menu(self.root, tearoff=0)
        self.jegy_context_menu.add_command(label="Törlés", command=self.jegy_torlese)

        uj_jegy_gomb = ttk.Button(table_and_button_container, text="Új jegy hozzáadása", command=self.uj_jegy_hozzadasa)
        uj_jegy_gomb.pack(pady=(10, 0))

        vissza_gomb = ttk.Button(main_keret, text="Vissza a főoldalra", command=self.vissza_a_fooldalra)
        vissza_gomb.pack(pady=10)

    def mutasd_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def mutasd_jegy_menu(self, event):
        item = self.jegyek_tree.identify_row(event.y)
        if item:
            self.jegyek_tree.selection_set(item)
            self.jegy_context_menu.post(event.x_root, event.y_root)

    def mutasd_jegyek_tab(self):
        kijelolt_elem = self.tree.focus()
        if not kijelolt_elem:
            return

        ertek = self.tree.item(kijelolt_elem, 'values')
        self.kivalasztott_diak_obj = keres_diak_azonosito_alapjan_MMR(ertek[1])

        if self.kivalasztott_diak_obj:
            self.jegyek_cimke.config(text=f"{self.kivalasztott_diak_obj.nev} ({self.kivalasztott_diak_obj.azonosito}) - {self.kivalasztott_diak_obj.szak}")
            
            for item in self.tantargy_tree.get_children():
                self.tantargy_tree.delete(item)
                
            tantargyak = TANTARGYAK_SZAKONKENT.get(self.kivalasztott_diak_obj.szak, [])
            for tantargy in tantargyak:
                tanulo_atlag = atlag_diaknak_tantargyra_MMR(self.kivalasztott_diak_obj.azonosito, tantargy)
                osztaly_atlag = osztalyatlag_tantargyra_MMR(tantargy)
                
                tanulo_atlag_str = f"{tanulo_atlag:.2f}" if tanulo_atlag > 0 else "N/A"
                osztaly_atlag_str = f"{osztaly_atlag:.2f}" if osztaly_atlag > 0 else "N/A"
                
                self.tantargy_tree.insert("", tk.END, values=(tantargy, tanulo_atlag_str, osztaly_atlag_str))
            
            for i in self.jegyek_tree.get_children():
                self.jegyek_tree.delete(i)
            
            self.naplo.tab(1, state="normal")
            self.naplo.select(1)

    def on_tantargy_kivalaszt(self, event):
        selection = self.tantargy_tree.selection()
        if selection:
            item_values = self.tantargy_tree.item(selection[0], 'values')
            self.kivalasztott_tantargy = item_values[0]
            self.frissit_jegyek_tablazat()

    def frissit_jegyek_tablazat(self):
        for i in self.jegyek_tree.get_children():
            self.jegyek_tree.delete(i)
        
        if not self.kivalasztott_diak_obj or not self.kivalasztott_tantargy:
            return
            
        jegyek = jegyek_betoltese_tantargyra_MMR(self.kivalasztott_diak_obj.azonosito, self.kivalasztott_tantargy)
        for jegy_adat in jegyek:
            self.jegyek_tree.insert("", tk.END, values=(jegy_adat['jegy'], jegy_adat['indoklas'], jegy_adat['datum']), iid=jegy_adat['id'])

    def uj_jegy_hozzadasa(self):
        if not self.kivalasztott_diak_obj or not self.kivalasztott_tantargy:
            messagebox.showwarning("Figyelmeztetés", "Először válassz ki egy tantárgyat!")
            return
            
        jegy_str = simpledialog.askstring("Új jegy", "Add meg a jegyet (1-5):", parent=self.root)
        if not jegy_str or not jegy_str.isdigit() or not (1 <= int(jegy_str) <= 5):
            messagebox.showerror("Hiba", "Érvénytelen jegy!")
            return
            
        indoklas = simpledialog.askstring("Új jegy", "Add meg az indoklást:", parent=self.root)
        if indoklas is None:
            return

        mai_datum = datetime.now().strftime("%Y-%m-%d")
        datum = simpledialog.askstring("Új jegy", "Add meg a dátumot (YYYY-MM-DD):", initialvalue=mai_datum, parent=self.root)
        if datum is None:
            return
            
        uj_jegy_hozzaadasa_MMR(self.kivalasztott_diak_obj.azonosito, self.kivalasztott_tantargy, int(jegy_str), indoklas, datum)

        self.frissit_jegyek_tablazat()
        self.frissit_diakok_listaja()
        self.mutasd_jegyek_tab()

        messagebox.showinfo("Siker", "Jegy sikeresen hozzáadva!")

    def jegy_torlese(self):
        kijelolt_elem = self.jegyek_tree.focus()
        if not kijelolt_elem:
            messagebox.showwarning("Figyelmeztetés", "Kérlek, válassz ki egy jegyet a törléshez!")
            return
            
        jegy_id = kijelolt_elem

        valasz = messagebox.askyesno("Megerősítés", "Biztosan törölni szeretnéd a kijelölt jegyet?")
        if valasz:
            jegy_torlese_MMR(jegy_id)

            self.frissit_jegyek_tablazat()
            self.frissit_diakok_listaja()
            self.mutasd_jegyek_tab()

            messagebox.showinfo("Siker", "Jegy törölve!")

    def vissza_a_fooldalra(self):
        self.naplo.select(0)
        self.naplo.tab(1, state="disabled")
        self.kivalasztott_diak_obj = None
        self.kivalasztott_tantargy = None

    def frissit_diakok_listaja(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        for diak in self.diakok:
            atlag = atlag_diaknak_MMR(diak.azonosito)
      
            self.tree.insert("", tk.END, values=(diak.nev, diak.azonosito, diak.szak, f"{atlag:.2f}"))

    def hozzaad_diak(self):
        nev = self.nev_entry.get()
        azonosito = self.azonosito_entry.get()
        szak = self.szak_combobox.get()

        if not nev or not azonosito or not szak:
            messagebox.showerror("Hiba", "A név, azonosító és szak mezők kötelezőek!")
            return

        if keres_diak_azonosito_alapjan_MMR(azonosito):
            messagebox.showerror("Hiba", "Ez az azonosító már létezik!")
            return

        uj_diak = Diak_MMR(nev, azonosito, szak)
        uj_diak_hozzaadasa_MMR(uj_diak)
        
        self.diakok.append(uj_diak)
        self.frissit_diakok_listaja()
        
        self.nev_entry.delete(0, tk.END)
        self.azonosito_entry.delete(0, tk.END)
        self.szak_combobox.current(0)
        
        messagebox.showinfo("Siker", f"{nev} sikeresen hozzáadva!")

    def torol_diak(self):
        kijelolt_elem = self.tree.focus()
        if not kijelolt_elem:
            messagebox.showwarning("Figyelmeztetés", "Kérlek, válassz ki egy diákot a törléshez!")
            return
        
        ertek = self.tree.item(kijelolt_elem, 'values')
        diak_nev = ertek[0]
        azonosito = ertek[1]
        
        valasz = messagebox.askyesno("Megerősítés", f"Biztosan törölni szeretnéd a következő diákot és minden jegyét?\n\n{diak_nev} ({azonosito})")
        if not valasz:
            return
        
        diak_torlese_MMR(azonosito)
        
        for diak in self.diakok:
            if diak.azonosito == azonosito:
                self.diakok.remove(diak)
                break
        
        self.frissit_diakok_listaja()

        messagebox.showinfo("Siker", f"{diak_nev} és minden jegye törölve lett!")