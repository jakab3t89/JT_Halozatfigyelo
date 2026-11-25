import tkinter as tk
from tkinter import ttk, messagebox
import socket
import csv
import time
from JT_halozat import JT_Celpont, JT_meres, JT_feloldas

CELPONT_FAJL = "celpontok.txt"
NAPLO_FAJL = "naplo.csv"


class JT_HalozatfigyeloApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JT Hálózatfigyelő")
        self.root.geometry("900x640")
        self.celpontok = []
        self.figyeles = False
        self.kovetkezo = 0
        self.naplo = []

        gep = socket.gethostname()
        tk.Label(root, text="JT HÁLÓZATFIGYELŐ", font=("Arial", 18, "bold")).pack(pady=(12, 2))
        tk.Label(root, text=f"Saját gép: {gep} ({JT_feloldas(gep)})", fg="gray").pack()

        bevitel = tk.Frame(root)
        bevitel.pack(pady=8)
        tk.Label(bevitel, text="Cím:").grid(row=0, column=0)
        self.cim_mezo = tk.Entry(bevitel, width=30)
        self.cim_mezo.grid(row=0, column=1, padx=5)
        tk.Label(bevitel, text="Port:").grid(row=0, column=2)
        self.port_mezo = tk.Entry(bevitel, width=8)
        self.port_mezo.insert(0, "443")
        self.port_mezo.grid(row=0, column=3, padx=5)
        tk.Button(bevitel, text="Hozzáadás", command=self.JT_hozzaadas).grid(row=0, column=4, padx=5)

        oszlopok = ("cim", "port", "ip", "allapot", "utolso", "atlag", "elerhetoseg")
        fejlecek = ("Cím", "Port", "IP-cím", "Állapot", "Utolsó (ms)", "Átlag (ms)", "Elérhetőség")
        self.tabla = ttk.Treeview(root, columns=oszlopok, show="headings", height=7)
        for oszlop, fejlec in zip(oszlopok, fejlecek):
            self.tabla.heading(oszlop, text=fejlec)
            self.tabla.column(oszlop, width=120, anchor="center")
        self.tabla.tag_configure("jo", foreground="green")
        self.tabla.tag_configure("rossz", foreground="red")
        self.tabla.pack(padx=10, fill="x")

        gombok = tk.Frame(root)
        gombok.pack(pady=8)
        self.inditas_gomb = tk.Button(gombok, text="Figyelés indítása", width=18, command=self.JT_inditas)
        self.inditas_gomb.grid(row=0, column=0, padx=5)
        tk.Button(gombok, text="Kijelölt törlése", width=18, command=self.JT_torles).grid(row=0, column=1, padx=5)
        tk.Button(gombok, text="Napló mentése", width=18, command=self.JT_naplo_mentes).grid(row=0, column=2, padx=5)

        self.grafikon = tk.Canvas(root, width=860, height=230, bg="white", highlightthickness=1, highlightbackground="gray")
        self.grafikon.pack(pady=5)

        self.allapotsor = tk.Label(root, text="Válassz ki egy célpontot a grafikonhoz.", anchor="w", fg="gray")
        self.allapotsor.pack(fill="x", padx=10)

        self.cim_mezo.bind("<Return>", lambda event: self.JT_hozzaadas())
        self.port_mezo.bind("<Return>", lambda event: self.JT_hozzaadas())
        self.tabla.bind("<Delete>", lambda event: self.JT_torles())
        self.tabla.bind("<<TreeviewSelect>>", lambda event: self.JT_rajzolas())
        self.root.protocol("WM_DELETE_WINDOW", self.JT_kilepes)

        self.JT_betoltes()
        self.JT_rajzolas()

    def JT_hozzaadas(self):
        cim = self.cim_mezo.get().strip()
        port = self.port_mezo.get().strip()
        if not cim or not port.isdigit() or not 0 < int(port) < 65536:
            messagebox.showerror("Hiba", "Adj meg egy címet és egy 1–65535 közötti portot!")
            return
        celpont = JT_Celpont(cim, int(port))
        self.celpontok.append(celpont)
        self.tabla.insert("", tk.END, values=celpont.JT_sor())
        self.cim_mezo.delete(0, tk.END)

    def JT_torles(self):
        kijelolt = self.tabla.selection()
        if not kijelolt:
            return
        index = self.tabla.index(kijelolt[0])
        self.tabla.delete(kijelolt[0])
        self.celpontok.pop(index)
        self.kovetkezo = 0
        self.JT_rajzolas()

    def JT_inditas(self):
        self.figyeles = not self.figyeles
        if self.figyeles:
            self.inditas_gomb.config(text="Figyelés leállítása")
            self.JT_utemezes()
        else:
            self.inditas_gomb.config(text="Figyelés indítása")

    def JT_utemezes(self):
        if not self.figyeles:
            return
        if self.celpontok:
            self.kovetkezo %= len(self.celpontok)
            celpont = self.celpontok[self.kovetkezo]
            ertek = JT_meres(celpont.cim, celpont.port)
            celpont.JT_rogzit(ertek)
            self.naplo.append((time.strftime("%Y-%m-%d %H:%M:%S"), celpont.cim, celpont.port, ertek if ertek is not None else "hiba"))
            self.JT_frissites(self.kovetkezo)
            self.kovetkezo += 1
        self.root.after(700, self.JT_utemezes)

    def JT_frissites(self, index):
        sor = self.tabla.get_children()[index]
        celpont = self.celpontok[index]
        cimke = "jo" if celpont.JT_allapot() == "elérhető" else "rossz"
        self.tabla.item(sor, values=celpont.JT_sor(), tags=(cimke,))
        kijelolt = self.tabla.selection()
        if kijelolt and kijelolt[0] == sor:
            self.JT_rajzolas()

    def JT_rajzolas(self):
        vaszon = self.grafikon
        vaszon.delete("all")
        szelesseg, magassag, margo = 860, 230, 40
        vaszon.create_line(margo, magassag - 25, szelesseg - 10, magassag - 25, fill="gray")
        vaszon.create_line(margo, 10, margo, magassag - 25, fill="gray")
        kijelolt = self.tabla.selection()
        if not kijelolt:
            vaszon.create_text(szelesseg / 2, magassag / 2, text="Nincs kijelölt célpont", fill="gray")
            return
        celpont = self.celpontok[self.tabla.index(kijelolt[0])]
        vaszon.create_text(szelesseg / 2, 12, text=f"{celpont.cim}:{celpont.port} válaszideje", font=("Arial", 10, "bold"))
        sikeres = celpont.JT_sikeres()
        if not celpont.meresek:
            vaszon.create_text(szelesseg / 2, magassag / 2, text="Még nincs mérés", fill="gray")
            return
        maximum = max(sikeres) if sikeres else 1
        vaszon.create_text(margo - 5, 25, text=f"{maximum:.0f}", anchor="e", font=("Arial", 8))
        vaszon.create_text(margo - 5, magassag - 25, text="0", anchor="e", font=("Arial", 8))
        lepes = (szelesseg - margo - 20) / 39
        elozo = None
        for i, ertek in enumerate(celpont.meresek):
            x = margo + 10 + i * lepes
            if ertek is None:
                vaszon.create_text(x, magassag - 35, text="✕", fill="red")
                elozo = None
                continue
            y = magassag - 25 - ertek / maximum * (magassag - 55)
            if elozo:
                vaszon.create_line(elozo[0], elozo[1], x, y, fill="royal blue", width=2)
            vaszon.create_oval(x - 3, y - 3, x + 3, y + 3, fill="royal blue", outline="")
            elozo = (x, y)
        self.allapotsor.config(text=f"{celpont.cim}: {len(celpont.meresek)} mérés, átlag {celpont.JT_atlag()} ms, elérhetőség {celpont.JT_elerhetoseg()}")

    def JT_naplo_mentes(self):
        if not self.naplo:
            messagebox.showinfo("Napló", "Még nincs mentendő mérés.")
            return
        with open(NAPLO_FAJL, "w", newline="", encoding="utf-8") as fajl:
            iro = csv.writer(fajl, delimiter=";")
            iro.writerow(["Időpont", "Cím", "Port", "Válaszidő (ms)"])
            iro.writerows(self.naplo)
        messagebox.showinfo("Napló", f"{len(self.naplo)} mérés elmentve: {NAPLO_FAJL}")

    def JT_betoltes(self):
        try:
            with open(CELPONT_FAJL, "r", encoding="utf-8") as fajl:
                for sor in fajl:
                    if ";" in sor:
                        cim, port = sor.strip().split(";")
                        celpont = JT_Celpont(cim, int(port))
                        self.celpontok.append(celpont)
                        self.tabla.insert("", tk.END, values=celpont.JT_sor())
        except FileNotFoundError:
            pass

    def JT_kilepes(self):
        with open(CELPONT_FAJL, "w", encoding="utf-8") as fajl:
            for celpont in self.celpontok:
                fajl.write(f"{celpont.cim};{celpont.port}\n")
        self.root.destroy()


root = tk.Tk()
app = JT_HalozatfigyeloApp(root)
root.mainloop()
