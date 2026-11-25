import tkinter as tk
from tkinter import ttk, messagebox
import socket
import csv
import time
from JT_halozat import JT_Celpont, JT_meres, JT_feloldas

CELPONT_FAJL = "celpontok.txt"
NAPLO_FAJL = "naplo.csv"
ESEMENY_FAJL = "esemenyek.txt"
SLO_CEL = 99
SZINEK = {"elérhető": "green", "lassú": "dark orange", "nem elérhető": "red", "várakozik": "gray"}


class JT_HalozatfigyeloApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JT Hálózatfigyelő – observability")
        self.root.geometry("980x740")
        self.celpontok = []
        self.figyeles = False
        self.kovetkezo = 0
        self.naplo = []

        gep = socket.gethostname()
        tk.Label(root, text="JT HÁLÓZATFIGYELŐ", font=("Arial", 18, "bold")).pack(pady=(10, 0))
        tk.Label(root, text=f"Mérőpont: {gep} ({JT_feloldas(gep)})  •  SLO-cél: {SLO_CEL}% elérhetőség", fg="gray").pack()

        bevitel = tk.Frame(root)
        bevitel.pack(pady=8)
        tk.Label(bevitel, text="Cím:").grid(row=0, column=0)
        self.cim_mezo = tk.Entry(bevitel, width=28)
        self.cim_mezo.grid(row=0, column=1, padx=5)
        tk.Label(bevitel, text="Port:").grid(row=0, column=2)
        self.port_mezo = tk.Entry(bevitel, width=7)
        self.port_mezo.insert(0, "443")
        self.port_mezo.grid(row=0, column=3, padx=5)
        tk.Button(bevitel, text="Hozzáadás", command=self.JT_hozzaadas).grid(row=0, column=4, padx=5)
        tk.Label(bevitel, text="Lassú, ha több mint (ms):").grid(row=0, column=5, padx=(20, 0))
        self.kuszob_mezo = tk.Entry(bevitel, width=6)
        self.kuszob_mezo.insert(0, "200")
        self.kuszob_mezo.grid(row=0, column=6, padx=5)

        oszlopok = ("cim", "port", "ip", "allapot", "utolso", "atlag", "p95", "elerhetoseg", "slo")
        fejlecek = ("Cím", "Port", "IP-cím", "Állapot", "Utolsó (ms)", "Átlag (ms)", "p95 (ms)", "Elérhetőség", "SLO")
        self.tabla = ttk.Treeview(root, columns=oszlopok, show="headings", height=7)
        for oszlop, fejlec in zip(oszlopok, fejlecek):
            self.tabla.heading(oszlop, text=fejlec)
            self.tabla.column(oszlop, width=105, anchor="center")
        for allapot, szin in SZINEK.items():
            self.tabla.tag_configure(allapot, foreground=szin)
        self.tabla.pack(padx=10, fill="x")

        gombok = tk.Frame(root)
        gombok.pack(pady=8)
        self.inditas_gomb = tk.Button(gombok, text="Figyelés indítása", width=18, command=self.JT_inditas)
        self.inditas_gomb.grid(row=0, column=0, padx=5)
        tk.Button(gombok, text="Kijelölt törlése", width=18, command=self.JT_torles).grid(row=0, column=1, padx=5)
        tk.Button(gombok, text="Napló mentése", width=18, command=self.JT_naplo_mentes).grid(row=0, column=2, padx=5)

        self.grafikon = tk.Canvas(root, width=940, height=200, bg="white", highlightthickness=1, highlightbackground="gray")
        self.grafikon.pack(pady=4)

        self.allapotsor = tk.Label(root, text="Válassz ki egy célpontot a grafikonhoz.", anchor="w", fg="gray")
        self.allapotsor.pack(fill="x", padx=12)

        tk.Label(root, text="Események (állapotváltozások)", font=("Arial", 10, "bold"), anchor="w").pack(fill="x", padx=12, pady=(6, 0))
        self.esemenyek = tk.Listbox(root, height=5)
        self.esemenyek.pack(fill="x", padx=10, pady=(0, 10))

        self.cim_mezo.bind("<Return>", lambda event: self.JT_hozzaadas())
        self.port_mezo.bind("<Return>", lambda event: self.JT_hozzaadas())
        self.kuszob_mezo.bind("<Return>", lambda event: self.JT_mindent_frissit())
        self.tabla.bind("<Delete>", lambda event: self.JT_torles())
        self.tabla.bind("<<TreeviewSelect>>", lambda event: self.JT_rajzolas())
        self.root.protocol("WM_DELETE_WINDOW", self.JT_kilepes)

        self.JT_betoltes()
        self.JT_rajzolas()

    def JT_kuszob(self):
        ertek = self.kuszob_mezo.get().strip()
        return int(ertek) if ertek.isdigit() and int(ertek) > 0 else 200

    def JT_hozzaadas(self):
        cim = self.cim_mezo.get().strip()
        port = self.port_mezo.get().strip()
        if not cim or not port.isdigit() or not 0 < int(port) < 65536:
            messagebox.showerror("Hiba", "Adj meg egy címet és egy 1–65535 közötti portot!")
            return
        celpont = JT_Celpont(cim, int(port))
        self.celpontok.append(celpont)
        self.tabla.insert("", tk.END, values=celpont.JT_sor(self.JT_kuszob(), SLO_CEL))
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
            self.JT_esemeny("ℹ", "Figyelés elindítva")
            self.JT_utemezes()
        else:
            self.inditas_gomb.config(text="Figyelés indítása")
            self.JT_esemeny("ℹ", "Figyelés leállítva")

    def JT_utemezes(self):
        if not self.figyeles:
            return
        if self.celpontok:
            self.kovetkezo %= len(self.celpontok)
            celpont = self.celpontok[self.kovetkezo]
            kuszob = self.JT_kuszob()
            elozo = celpont.JT_allapot(kuszob)
            ertek = JT_meres(celpont.cim, celpont.port)
            celpont.JT_rogzit(ertek)
            uj = celpont.JT_allapot(kuszob)
            if uj != elozo and not (elozo == "várakozik" and uj == "elérhető"):
                self.JT_allapotvaltas(celpont, uj, ertek)
            self.naplo.append((time.strftime("%Y-%m-%d %H:%M:%S"), celpont.cim, celpont.port,
                               ertek if ertek is not None else "", uj))
            self.JT_frissites(self.kovetkezo)
            self.kovetkezo += 1
        self.root.after(700, self.JT_utemezes)

    def JT_allapotvaltas(self, celpont, allapot, ertek):
        nev = f"{celpont.cim}:{celpont.port}"
        if allapot == "nem elérhető":
            self.JT_esemeny("✖", f"{nev} nem elérhető – kiesés kezdete")
        elif allapot == "lassú":
            self.JT_esemeny("⚠", f"{nev} lassú: {ertek} ms (küszöb: {self.JT_kuszob()} ms)")
        else:
            self.JT_esemeny("✔", f"{nev} helyreállt: {ertek} ms")

    def JT_esemeny(self, jel, szoveg):
        sor = f"{time.strftime('%H:%M:%S')}  {jel}  {szoveg}"
        self.esemenyek.insert(0, sor)
        szin = {"✖": "red", "⚠": "dark orange", "✔": "green"}.get(jel, "gray")
        self.esemenyek.itemconfig(0, foreground=szin)
        with open(ESEMENY_FAJL, "a", encoding="utf-8") as fajl:
            fajl.write(f"{time.strftime('%Y-%m-%d')} {sor}\n")

    def JT_frissites(self, index):
        sor = self.tabla.get_children()[index]
        celpont = self.celpontok[index]
        kuszob = self.JT_kuszob()
        self.tabla.item(sor, values=celpont.JT_sor(kuszob, SLO_CEL), tags=(celpont.JT_allapot(kuszob),))
        kijelolt = self.tabla.selection()
        if kijelolt and kijelolt[0] == sor:
            self.JT_rajzolas()

    def JT_mindent_frissit(self):
        for index in range(len(self.celpontok)):
            self.JT_frissites(index)
        self.JT_rajzolas()

    def JT_rajzolas(self):
        vaszon = self.grafikon
        vaszon.delete("all")
        szelesseg, magassag, margo = 940, 200, 45
        also = magassag - 25
        vaszon.create_line(margo, also, szelesseg - 10, also, fill="gray")
        vaszon.create_line(margo, 10, margo, also, fill="gray")
        kijelolt = self.tabla.selection()
        if not kijelolt:
            vaszon.create_text(szelesseg / 2, magassag / 2, text="Nincs kijelölt célpont", fill="gray")
            return
        celpont = self.celpontok[self.tabla.index(kijelolt[0])]
        kuszob = self.JT_kuszob()
        vaszon.create_text(szelesseg / 2, 12, text=f"{celpont.cim}:{celpont.port} válaszideje", font=("Arial", 10, "bold"))
        if not celpont.meresek:
            vaszon.create_text(szelesseg / 2, magassag / 2, text="Még nincs mérés", fill="gray")
            return
        maximum = max(celpont.JT_sikeres() + [kuszob]) * 1.1
        magassag_ms = lambda ms: also - ms / maximum * (also - 25)
        vaszon.create_line(margo, magassag_ms(kuszob), szelesseg - 10, magassag_ms(kuszob), fill="dark orange", dash=(5, 3))
        vaszon.create_text(szelesseg - 12, magassag_ms(kuszob) - 8, text=f"küszöb {kuszob} ms", anchor="e", fill="dark orange", font=("Arial", 8))
        vaszon.create_text(margo - 5, 25, text=f"{maximum:.0f}", anchor="e", font=("Arial", 8))
        vaszon.create_text(margo - 5, also, text="0", anchor="e", font=("Arial", 8))
        lepes = (szelesseg - margo - 20) / 39
        elozo = None
        for i, ertek in enumerate(celpont.meresek):
            x = margo + 10 + i * lepes
            if ertek is None:
                vaszon.create_text(x, also - 10, text="✕", fill="red")
                elozo = None
                continue
            y = magassag_ms(ertek)
            if elozo:
                vaszon.create_line(elozo[0], elozo[1], x, y, fill="royal blue", width=2)
            szin = "dark orange" if ertek > kuszob else "royal blue"
            vaszon.create_oval(x - 3, y - 3, x + 3, y + 3, fill=szin, outline="")
            elozo = (x, y)
        self.allapotsor.config(text=f"{celpont.cim}: {len(celpont.meresek)} mérés  •  átlag {celpont.JT_atlag()} ms  •  "
                                    f"p95 {celpont.JT_p95()} ms  •  elérhetőség {celpont.JT_elerhetoseg()}  •  SLO {celpont.JT_slo(SLO_CEL)}")

    def JT_naplo_mentes(self):
        if not self.naplo:
            messagebox.showinfo("Napló", "Még nincs mentendő mérés.")
            return
        with open(NAPLO_FAJL, "w", newline="", encoding="utf-8") as fajl:
            iro = csv.writer(fajl, delimiter=";")
            iro.writerow(["Időpont", "Cím", "Port", "Válaszidő (ms)", "Állapot"])
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
                        self.tabla.insert("", tk.END, values=celpont.JT_sor(self.JT_kuszob(), SLO_CEL))
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
