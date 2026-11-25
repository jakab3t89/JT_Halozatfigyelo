# JT Hálózatfigyelő

**Hallgató:** Jakab Tibor – CFFA3D  
**Tantárgy:** Szkript nyelvek (Python) – projektfeladat  
**Tagozat:** levelező

## Feladat leírása

A JT Hálózatfigyelő egy grafikus felületű, observability szemléletű program, amely szerverek és szolgáltatások elérhetőségét és válaszidejét figyeli. A felhasználó megad egy címet (pl. `github.com`) és egy portot (pl. `443`). A figyelés indítása után a program sorban, folyamatosan kapcsolódik minden célponthoz, és méri, mennyi idő alatt jön létre a kapcsolat.

A program a mérésekből:

- állapotot ad minden célpontra: **elérhető** (zöld), **lassú** (narancs, ha a válaszidő a beállított küszöb fölött van), **nem elérhető** (piros),
- kiszámolja az utolsó, az átlagos és a **p95** válaszidőt,
- kiszámolja az **elérhetőséget** százalékban, és jelzi, hogy teljesül-e a **99%-os SLO-cél**,
- **eseményt** naplóz minden állapotváltozásnál (kiesés, lassulás, helyreállás),
- élő **grafikont** rajzol a kijelölt célpont válaszidejéről, a küszöbvonallal együtt,
- a méréseket **CSV-naplóba**, az eseményeket szövegfájlba menti.

## Miért observability?

Rendszerintegrációs mérnökként dolgozom a MÁV Szolgáltató Központ Zrt.-nél, és a munkaköröm egyik kiemelt területe az observability: a vasúti üzemi rendszerek (többek között GVK, ETR, JÉ, MÁV+, EMIG, Pass2) Dynatrace Managed alapú felügyelete. Több mint 14 környezet monitorozási infrastruktúráját üzemeltetem, problémákat elemzek a válaszidő-, hiba- és adatbázis-metrikák alapján, és az Observability Hungary 2026 konferencián társelőadóként mutattuk be a MÁV nyolcéves Dynatrace-monitorozási útját.

A projektben ennek a szemléletnek az alapjait valósítottam meg kicsiben, Pythonban. Ugyanazokat a fogalmakat használja, mint a nagyvállalati eszközök:

| Fogalom | A programban | Mire jó |
|---|---|---|
| Szintetikus mérés | `JT_meres()` – időzített TCP-kapcsolódás | a szolgáltatást kívülről, a felhasználó szemszögéből ellenőrzi |
| Válaszidő (latency) | utolsó és átlagos válaszidő | megmutatja, milyen gyors a szolgáltatás |
| p95 | `JT_p95()` | a mérések 95%-a ennél gyorsabb; az átlag elfedi a ritka, de nagy lassulásokat, a p95 nem |
| Elérhetőség | sikeres / összes mérés | megmutatja, a mérések hány százalékában válaszolt a szolgáltatás |
| SLO | 99%-os cél, „teljesül / sérül” | előre rögzített minőségi cél, amihez a mért értéket hasonlítjuk |
| Küszöb, riasztás | „Lassú, ha több mint (ms)” | nem csak a teljes kiesés számít hibának, a lassúság is |
| Esemény (problem) | kiesés kezdete, lassulás, helyreállás | csak az állapotváltozást jelzi, nem minden mérést, így nincs „riasztási zaj” |

## Program felépítése

- Indítás: `main.py`
- Alapablak: `root = tk.Tk()`
- Programnév: `app = JT_HalozatfigyeloApp(root)`

## Fájlok

- `main.py` – a program indítása és a grafikus felület (`JT_HalozatfigyeloApp` osztály)
- `JT_halozat.py` – saját modul: a mérés, a névfeloldás és a `JT_Celpont` osztály
- `celpontok.txt` – a figyelt célpontok listája (`cím;port` soronként)
- `naplo.csv` – a mentett mérések (a „Napló mentése” gomb hozza létre)
- `esemenyek.txt` – az állapotváltozások naplója (a program folyamatosan írja)

## Modulok és a modulokban használt függvények

**Tanult modul – `tkinter` (és `tkinter.ttk`, `tkinter.messagebox`)**

- `tk.Tk()`, `title()`, `geometry()`, `protocol()` – alapablak
- `tk.Label()`, `tk.Entry()`, `tk.Button()`, `tk.Frame()`, `tk.Listbox()` – felületi elemek
- `ttk.Treeview()`, `heading()`, `column()`, `insert()`, `item()`, `selection()`, `index()`, `tag_configure()` – táblázat
- `tk.Canvas()`, `create_line()`, `create_oval()`, `create_text()`, `delete()` – grafikon rajzolása
- `itemconfig()` – az eseménysorok színezése
- `pack()`, `grid()` – elhelyezés
- `bind()` – eseménykezelés
- `after()` – időzített, ismétlődő mérés
- `messagebox.showerror()`, `messagebox.showinfo()` – üzenetek
- `mainloop()` – eseményciklus

**Bemutatandó modul – `socket`**

- `socket.gethostname()` – a saját gép (a mérőpont) nevét adja vissza
- `socket.gethostbyname()` – névfeloldás: egy címhez megadja az IP-címet
- `socket.create_connection()` – TCP-kapcsolatot nyit a megadott címre és portra; ha sikerül, a szolgáltatás elérhető

**További szabványos modulok**

- `time.perf_counter()` – a válaszidő pontos mérése
- `time.strftime()` – időbélyeg a naplóhoz és az eseményekhez
- `statistics.mean()` – átlagos válaszidő
- `statistics.quantiles()` – p95 válaszidő
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
- `JT_p95()` – 95. percentilis válaszidő
- `JT_elerhetoseg_szazalek()`, `JT_elerhetoseg()` – elérhetőség számként és szövegként
- `JT_slo(cel)` – teljesül-e az SLO-cél
- `JT_allapot(kuszob)` – elérhető / lassú / nem elérhető / várakozik
- `JT_sor(kuszob, cel)` – a táblázat egy sorának adatai

**`JT_HalozatfigyeloApp`** (`main.py`) – a program ablaka és működése.

- `JT_kuszob()` – a beállított válaszidő-küszöb beolvasása
- `JT_hozzaadas()` – új célpont felvétele, a bevitt adatok ellenőrzése
- `JT_torles()` – a kijelölt célpont törlése
- `JT_inditas()` – a figyelés indítása és leállítása
- `JT_utemezes()` – 0,7 másodpercenként megméri a soron következő célpontot, és figyeli az állapotváltozást
- `JT_allapotvaltas()` – az állapotváltozásból eseményszöveget készít
- `JT_esemeny()` – eseményt ír a listába és az `esemenyek.txt` fájlba
- `JT_frissites(index)`, `JT_mindent_frissit()` – a táblázat frissítése
- `JT_rajzolas()` – a kijelölt célpont grafikonja a küszöbvonallal
- `JT_naplo_mentes()` – CSV-napló mentése
- `JT_betoltes()` – a célpontok betöltése induláskor
- `JT_kilepes()` – a célpontok mentése kilépéskor

## Eseménykezelés

- Gombok (`command`): Hozzáadás, Figyelés indítása/leállítása, Kijelölt törlése, Napló mentése
- `<Return>` – Enterrel is felvehető új célpont; a küszöb mezőben Enterre azonnal újraszámolja az állapotokat
- `<Delete>` – a kijelölt sor Delete billentyűvel törölhető
- `<<TreeviewSelect>>` – sor kijelölésekor a grafikon átvált az adott célpontra
- `WM_DELETE_WINDOW` – az ablak bezárásakor a program elmenti a célpontokat
- `after()` – időzítő, amely a figyelés alatt folyamatosan újraütemezi a mérést

## Futtatás

1. Python 3.8 vagy újabb szükséges, külön csomagot nem kell telepíteni (minden modul a Python része).
2. A `main.py`, a `JT_halozat.py` és a `celpontok.txt` legyen egy mappában.
3. Indítás: `python main.py` (vagy PyCharmból).
4. Kattints a „Figyelés indítása” gombra, majd jelölj ki egy sort a grafikonhoz.

Tipp a bemutatáshoz: ha a küszöböt alacsonyra (pl. 20 ms) állítod, a lassulás- és helyreállás-események azonnal megjelennek. A `localhost:8080` célpont szándékosan szerepel a listában: ha a gépen nem fut semmi a 8080-as porton, ezen látszik, hogyan néz ki egy kiesés.
