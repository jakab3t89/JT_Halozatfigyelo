# JT Hálózatfigyelő

**Hallgató:** Jakab Tibor
**Tantárgy:** Szkript nyelvek (Python) – projektfeladat
**Tagozat:** nappali

## Feladat leírása

A JT Hálózatfigyelő egy grafikus felületű program, amely szerverek és szolgáltatások elérhetőségét figyeli. A felhasználó megad egy címet (pl. `google.com`) és egy portot (pl. `443`), a program pedig a figyelés indítása után sorban, folyamatosan megpróbál kapcsolódni minden célponthoz.

Minden célpontnál megjelenik:

- az IP-cím (névfeloldással),
- az állapot (zöld: elérhető, piros: nem elérhető),
- az utolsó és az átlagos válaszidő milliszekundumban,
- az elérhetőség százalékban.

A táblázatban kijelölt célpont válaszidejéről a program élő grafikont rajzol: a kék vonal a sikeres méréseket, a piros ✕ a sikerteleneket mutatja. A mérések CSV-naplóba menthetők. A célpontok listáját a program kilépéskor elmenti, és induláskor visszatölti.

## Program felépítése

- Indítás: `main.py`
- Alapablak: `root = tk.Tk()`
- Programnév: `app = JT_HalozatfigyeloApp(root)`

## Fájlok

- `main.py` – a program indítása és a grafikus felület (`JT_HalozatfigyeloApp` osztály)
- `JT_halozat.py` – saját modul: a mérés, a névfeloldás és a `JT_Celpont` osztály
- `celpontok.txt` – a figyelt célpontok listája (`cím;port` soronként)
- `naplo.csv` – a mentett mérések (a „Napló mentése” gomb hozza létre)

## Modulok és a modulokban használt függvények

**Tanult modul – `tkinter` (és `tkinter.ttk`, `tkinter.messagebox`)**

- `tk.Tk()`, `title()`, `geometry()`, `protocol()` – alapablak
- `tk.Label()`, `tk.Entry()`, `tk.Button()`, `tk.Frame()` – felületi elemek
- `ttk.Treeview()`, `heading()`, `column()`, `insert()`, `item()`, `selection()`, `index()`, `tag_configure()` – táblázat
- `tk.Canvas()`, `create_line()`, `create_oval()`, `create_text()`, `delete()` – grafikon rajzolása
- `pack()`, `grid()` – elhelyezés
- `bind()` – eseménykezelés
- `after()` – időzített, ismétlődő mérés
- `messagebox.showerror()`, `messagebox.showinfo()` – üzenetek
- `mainloop()` – eseményciklus

**Bemutatandó modul – `socket`**

- `socket.gethostname()` – a saját gép nevét adja vissza
- `socket.gethostbyname()` – névfeloldás: egy címhez megadja az IP-címet
- `socket.create_connection()` – TCP-kapcsolatot nyit a megadott címre és portra; ha sikerül, a szolgáltatás elérhető

**További szabványos modulok**

- `time.perf_counter()` – a válaszidő pontos mérése
- `time.strftime()` – időbélyeg a naplóhoz
- `statistics.mean()` – átlagos válaszidő
- `csv.writer()`, `writerow()`, `writerows()` – a napló mentése CSV-fájlba

**Saját modul – `JT_halozat`**

- `JT_meres(cim, port, idotullepes)` – megméri, mennyi idő alatt jön létre a kapcsolat; sikertelenség esetén `None`
- `JT_feloldas(cim)` – IP-címet ad vissza, hiba esetén „ismeretlen”
- `JT_Celpont` osztály (lásd lent)

## Osztályok

**`JT_Celpont`** (`JT_halozat.py`) – egy figyelt célpont adatai: cím, port, IP-cím és az utolsó 40 mérés.

- `JT_rogzit(ertek)` – új mérés hozzáadása
- `JT_sikeres()` – a sikeres mérések listája
- `JT_atlag()` – átlagos válaszidő
- `JT_elerhetoseg()` – elérhetőség százalékban
- `JT_allapot()` – elérhető / nem elérhető / várakozik
- `JT_sor()` – a táblázat egy sorának adatai

**`JT_HalozatfigyeloApp`** (`main.py`) – a program ablaka és működése.

- `JT_hozzaadas()` – új célpont felvétele, a bevitt adatok ellenőrzése
- `JT_torles()` – a kijelölt célpont törlése
- `JT_inditas()` – a figyelés indítása és leállítása
- `JT_utemezes()` – 0,7 másodpercenként megméri a soron következő célpontot
- `JT_frissites(index)` – frissíti a táblázat sorát és a színét
- `JT_rajzolas()` – megrajzolja a kijelölt célpont grafikonját
- `JT_naplo_mentes()` – CSV-napló mentése
- `JT_betoltes()` – a célpontok betöltése induláskor
- `JT_kilepes()` – a célpontok mentése kilépéskor

## Eseménykezelés

- Gombok (`command`): Hozzáadás, Figyelés indítása/leállítása, Kijelölt törlése, Napló mentése
- `<Return>` – Enterrel is felvehető új célpont
- `<Delete>` – a kijelölt sor Delete billentyűvel törölhető
- `<<TreeviewSelect>>` – sor kijelölésekor a grafikon átvált az adott célpontra
- `WM_DELETE_WINDOW` – az ablak bezárásakor a program elmenti a célpontokat
- `after()` – időzítő, amely a figyelés alatt folyamatosan újraütemezi a mérést

## Futtatás

1. Python 3 szükséges, külön csomagot nem kell telepíteni (minden modul a Python része).
2. A `main.py`, a `JT_halozat.py` és a `celpontok.txt` legyen egy mappában.
3. Indítás: `python main.py` (vagy PyCharmból).
4. Kattints a „Figyelés indítása” gombra, majd jelölj ki egy sort a grafikonhoz.

A `localhost;8080` célpont szándékosan szerepel a listában: ha a gépen nem fut semmi a 8080-as porton, ezen látszik, hogyan jelenik meg egy nem elérhető szolgáltatás.
