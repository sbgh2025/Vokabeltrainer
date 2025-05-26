import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import random
import csv
import subprocess

DB_PATH = "/path/to/project/src/vokabeln.db"

print(f"[INFO] Verwende Datenbank: {DB_PATH}")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS vokabeln (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        englisch TEXT,
        deutsch TEXT,
        UNIQUE (englisch, deutsch)
    )
    ''')
    conn.commit()
    conn.close()

def speichere_vokabel(englisch, deutsch):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO vokabeln (englisch, deutsch) VALUES (?, ?)", (englisch, deutsch))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Doppeltes Wortpaar bereits vorhanden
        return False

def delete_vokabel(englisch):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM vokabeln WHERE englisch=?", (englisch,))
    conn.commit()
    conn.close()

def get_all_vokabeln():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT englisch, deutsch FROM vokabeln")
    result = c.fetchall()
    conn.close()
    return result

def import_csv(path):
    count = 0
    skipped = 0
    print(f"[INFO] Starte CSV-Import von: {path}")
    with open(path, newline='', encoding='utf-8') as csvfile:
        try:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect)
        except:
            csvfile.seek(0)
            reader = csv.reader(csvfile)

        for row in reader:
            print(f"[CSV-Zeile] {row}")
            if len(row) >= 2:
                if speichere_vokabel(row[0].strip(), row[1].strip()):
                    count += 1
                else:
                    print(f"[WARNUNG] Duplikat übersprungen: {row}")
                    skipped += 1
            else:
                print(f"[WARNUNG] Ungültige Zeile übersprungen: {row}")
                skipped += 1
    print(f"[INFO] {count} Vokabeln importiert, {skipped} Zeilen übersprungen.")
    return count

def get_random_vokabel():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT englisch, deutsch FROM vokabeln ORDER BY RANDOM() LIMIT 1")
    result = c.fetchone()
    conn.close()
    return result

class VokabelSpiel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vokabeltrainer")
        self.geometry("800x600")

        self.score = 0
        self.liste_ausgeklappt = False

        self.frm_verwaltung = tk.Frame(self)
        self.frm_spiel = tk.Frame(self)

        self.frm_verwaltung.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        self.frm_spiel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.sterne_label_var = tk.StringVar(value="Sterne: 0")
        self.sterne_label = tk.Label(self.frm_spiel, textvariable=self.sterne_label_var, font=("Arial", 16))
        self.sterne_label.pack(anchor="ne", padx=10, pady=5)

        self.create_verwaltungsbereich()
        self.create_spielbereich()

        self.vokabel_mitte = None
        self.richtige_antwort = None

        self.deutsch_worte = []
        self.animieren = False

        # Liste beim Start zugeklappt setzen (nicht toggle)
        self.liste_zugeklappt_setzen()

    def create_verwaltungsbereich(self):
        frm = self.frm_verwaltung

        tk.Label(frm, text="Englisch:").grid(row=0, column=0, sticky="w")
        self.entry_englisch = tk.Entry(frm)
        self.entry_englisch.grid(row=0, column=1, sticky="we")

        tk.Label(frm, text="Deutsch:").grid(row=0, column=2, sticky="w")
        self.entry_deutsch = tk.Entry(frm)
        self.entry_deutsch.grid(row=0, column=3, sticky="we")

        btn_add = tk.Button(frm, text="Hinzufügen", command=self.add_vokabel)
        btn_add.grid(row=0, column=4, padx=5, sticky="we")

        self.textfeld = tk.Text(frm, height=1, width=40)
        self.textfeld.grid(row=1, column=0, columnspan=4, sticky="we", pady=10)
        self.textfeld.config(state=tk.DISABLED)
        self.textfeld.bind("<Button-1>", self.toggle_textfeld)

        self.pfeil_button = tk.Button(frm, text="▲", width=2, command=self.toggle_textfeld)
        self.pfeil_button.grid(row=1, column=4, sticky="w")

        self.listbox_vokabeln = tk.Listbox(frm, height=10)
        self.listbox_vokabeln.grid(row=2, column=0, columnspan=5, sticky="we", pady=(0,10))

        btn_refresh = tk.Button(frm, text="Liste aktualisieren", command=self.vokabel_liste_aktualisieren)
        btn_refresh.grid(row=3, column=0, sticky="we")

        btn_del_selected = tk.Button(frm, text="Ausgewählte löschen", command=self.loesche_ausgewaehlte_vokabel)
        btn_del_selected.grid(row=3, column=1, sticky="we")

        btn_import = tk.Button(frm, text="CSV importieren", command=self.csv_import)
        btn_import.grid(row=3, column=2, sticky="we")

        for i in range(5):
            frm.grid_columnconfigure(i, weight=1)

        self.vokabel_liste_aktualisieren()
        self.zeige_erstes_wortpaar()
        # self.toggle_textfeld()  # NICHT mehr toggle, sondern explizit zugeklappt

    def liste_zugeklappt_setzen(self):
        # Liste explizit zugeklappt setzen (ohne toggle)
        if self.liste_ausgeklappt:  # falls offen, dann zuklappen
            self.listbox_vokabeln.grid_remove()
            self.pfeil_button.config(text="▼")
            self.liste_ausgeklappt = False
        else:
            # Falls schon zugeklappt, nichts tun
            self.listbox_vokabeln.grid_remove()
            self.pfeil_button.config(text="▼")
            self.liste_ausgeklappt = False

    def zeige_erstes_wortpaar(self):
        alle = get_all_vokabeln()
        if alle:
            erstes_paar = alle[0]
            text = f"{erstes_paar[0]} - {erstes_paar[1]}"
        else:
            text = ""
        self.textfeld.config(state=tk.NORMAL)
        self.textfeld.delete("1.0", tk.END)
        self.textfeld.insert(tk.END, text)
        self.textfeld.config(state=tk.DISABLED)

    def toggle_textfeld(self, event=None):
        if self.liste_ausgeklappt:
            self.listbox_vokabeln.grid_remove()
            self.pfeil_button.config(text="▼")
            self.liste_ausgeklappt = False
        else:
            self.listbox_vokabeln.grid()
            self.pfeil_button.config(text="▲")
            self.liste_ausgeklappt = True

    def vokabel_liste_aktualisieren(self):
        print("[INFO] Aktualisiere Vokabelliste...")
        self.listbox_vokabeln.delete(0, tk.END)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT englisch, deutsch FROM vokabeln ORDER BY englisch COLLATE NOCASE ASC")
        vokabeln = c.fetchall()
        conn.close()
        for eng, deu in vokabeln:
            print(f"[LISTE] {eng} - {deu}")
            self.listbox_vokabeln.insert(tk.END, f"{eng} - {deu}")

    def loesche_ausgewaehlte_vokabel(self):
        auswahl = self.listbox_vokabeln.curselection()
        if not auswahl:
            messagebox.showwarning("Fehler", "Bitte erst eine Vokabel auswählen.")
            return

        eintrag = self.listbox_vokabeln.get(auswahl[0])
        englisch = eintrag.split(" - ")[0]

        delete_vokabel(englisch)
        messagebox.showinfo("Gelöscht", f"Vokabel '{englisch}' wurde gelöscht.")
        self.vokabel_liste_aktualisieren()
        self.zeige_erstes_wortpaar()

    def add_vokabel(self):
        eng = self.entry_englisch.get().strip()
        deu = self.entry_deutsch.get().strip()
        if eng and deu:
            if speichere_vokabel(eng, deu):
                messagebox.showinfo("Erfolg", f"Vokabelpaar '{eng} - {deu}' hinzugefügt.")
                self.vokabel_liste_aktualisieren()
                self.zeige_erstes_wortpaar()
                self.entry_englisch.delete(0, tk.END)
                self.entry_deutsch.delete(0, tk.END)
            else:
                messagebox.showwarning("Fehler", "Dieses Wortpaar ist bereits vorhanden.")
        else:
            messagebox.showwarning("Fehler", "Bitte beide Felder ausfüllen.")

    def csv_import(self):
        path = filedialog.askopenfilename(title="CSV-Datei auswählen", filetypes=[("CSV Dateien", "*.csv")])
        if path:
            anzahl = import_csv(path)
            messagebox.showinfo("Import abgeschlossen", f"{anzahl} Vokabelpaare importiert.")
            self.vokabel_liste_aktualisieren()
            self.zeige_erstes_wortpaar()

    def create_spielbereich(self):
        self.canvas = tk.Canvas(self.frm_spiel, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.btn_start = tk.Button(self.frm_spiel, text="Start", command=self.start_neue_runde)
        self.btn_start.pack(pady=5)

        # Button für Sprachausgabe des englischen Wortes
        self.btn_ausgabe = tk.Button(self.frm_spiel, text="Englisches Wort sprechen", command=self.sprache_ausgeben)
        self.btn_ausgabe.pack(pady=5)

        self.canvas.bind("<Button-1>", self.on_canvas_click)

    def on_canvas_resize(self, event):
        self.mitte_x = self.canvas.winfo_width() // 2
        self.mitte_y = self.canvas.winfo_height() // 2

    def wort_ausgewaehlt(self, wort):
        self.animieren = False  # Bewegung immer stoppen – egal ob richtig oder falsch
        if wort == self.richtige_antwort:
            self.score += 1
            self.sterne_label_var.set(f"Sterne: {self.score}")
            messagebox.showinfo("Richtig!", "Das war richtig!")
        else:
            messagebox.showwarning("Falsch!", f"Falsch! Die richtige Übersetzung ist: {self.richtige_antwort}")
        self.btn_start.pack(pady=5)  # Startbutton wieder anzeigen

    def start_neue_runde(self):
        self.canvas.delete("all")
        self.deutsch_worte.clear()
        self.animieren = False

        vok = get_random_vokabel()
        if vok is None:
            messagebox.showwarning("Keine Vokabeln", "Bitte erst Vokabeln hinzufügen.")
            return
        englisch, deutsch = vok
        self.vokabel_mitte = englisch
        self.richtige_antwort = deutsch

        self.canvas.create_rectangle(
            self.mitte_x - 100,
            self.mitte_y - 50,
            self.mitte_x + 100,
            self.mitte_y + 50,
            fill="lightblue", tags="mitte_rechteck"
        )
        self.canvas.create_text(self.mitte_x, self.mitte_y, text=englisch, font=("Arial", 24), tags="mitte_text")

        alle = get_all_vokabeln()
        deutsche_worte = set([d for _, d in alle if d != deutsch])
        falsche = random.sample(list(deutsche_worte), min(3, len(deutsche_worte))) if len(deutsche_worte) >= 3 else list(deutsche_worte)
        alle_optionen = falsche + [deutsch]
        random.shuffle(alle_optionen)

        startpunkte = [
            (10, random.randint(50, 550)),
            (790, random.randint(50, 550)),
            (random.randint(50, 750), 10),
            (random.randint(50, 750), 590)
        ]

        self.deutsch_worte = []
        for i, wort in enumerate(alle_optionen):
            x0, y0 = startpunkte[i]
            # viel langsamere Bewegung
            dx = (self.mitte_x - x0) / 2000
            dy = (self.mitte_y - y0) / 2000
            text_id = self.canvas.create_text(x0, y0, text=wort, font=("Arial", 16), fill="black", tags="deutsch")
            self.deutsch_worte.append({
                "text": wort,
                "x": x0,
                "y": y0,
                "dx": dx,
                "dy": dy,
                "id": text_id
            })

        self.animieren = True
        self.animate()
        self.btn_start.pack_forget()

    def animate(self):
        if not self.animieren:
            return
        alle_fertig = True
        for wort in self.deutsch_worte:
            if abs(wort["x"] - self.mitte_x) > abs(wort["dx"]) or abs(wort["y"] - self.mitte_y) > abs(wort["dy"]):
                wort["x"] += wort["dx"]
                wort["y"] += wort["dy"]
                self.canvas.coords(wort["id"], wort["x"], wort["y"])
                alle_fertig = False
        if not alle_fertig:
            self.after(20, self.animate)
        else:
            # Animation fertig - Wort anklickbar
            pass

    def on_canvas_click(self, event):
        x, y = event.x, event.y
        items = self.canvas.find_overlapping(x, y, x, y)
        for item in items:
            for wort in self.deutsch_worte:
                if wort["id"] == item:
                    self.wort_ausgewaehlt(wort["text"])
                    return

    def sprache_ausgeben(self):
        if self.vokabel_mitte:
            # Beispiel mit espeak, auf Linux
            subprocess.Popen(['espeak', self.vokabel_mitte])

if __name__ == "__main__":
    init_db()
    app = VokabelSpiel()
    app.mainloop()
