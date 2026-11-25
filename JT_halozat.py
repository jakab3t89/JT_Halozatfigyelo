import socket
import time
import statistics


def JT_meres(cim, port, idotullepes=0.5):
    kezdes = time.perf_counter()
    try:
        kapcsolat = socket.create_connection((cim, port), timeout=idotullepes)
        kapcsolat.close()
    except OSError:
        return None
    return round((time.perf_counter() - kezdes) * 1000, 1)


def JT_feloldas(cim):
    try:
        return socket.gethostbyname(cim)
    except OSError:
        return "ismeretlen"


class JT_Celpont:
    def __init__(self, cim, port):
        self.cim = cim
        self.port = port
        self.ip = JT_feloldas(cim)
        self.meresek = []

    def JT_rogzit(self, ertek):
        self.meresek.append(ertek)
        if len(self.meresek) > 40:
            self.meresek.pop(0)
        if ertek is not None and self.ip == "ismeretlen":
            self.ip = JT_feloldas(self.cim)

    def JT_sikeres(self):
        return [m for m in self.meresek if m is not None]

    def JT_atlag(self):
        sikeres = self.JT_sikeres()
        if not sikeres:
            return "-"
        return round(statistics.mean(sikeres), 1)

    def JT_p95(self):
        sikeres = self.JT_sikeres()
        if not sikeres:
            return "-"
        if len(sikeres) == 1:
            return sikeres[0]
        return round(statistics.quantiles(sikeres, n=20, method="inclusive")[-1], 1)

    def JT_elerhetoseg_szazalek(self):
        if not self.meresek:
            return None
        return len(self.JT_sikeres()) / len(self.meresek) * 100

    def JT_elerhetoseg(self):
        szazalek = self.JT_elerhetoseg_szazalek()
        return "-" if szazalek is None else f"{round(szazalek)}%"

    def JT_slo(self, cel):
        szazalek = self.JT_elerhetoseg_szazalek()
        if szazalek is None:
            return "-"
        return "teljesül" if szazalek >= cel else "sérül"

    def JT_allapot(self, kuszob):
        if not self.meresek:
            return "várakozik"
        utolso = self.meresek[-1]
        if utolso is None:
            return "nem elérhető"
        return "lassú" if utolso > kuszob else "elérhető"

    def JT_sor(self, kuszob, cel):
        utolso = self.meresek[-1] if self.meresek and self.meresek[-1] is not None else "-"
        return (self.cim, self.port, self.ip, self.JT_allapot(kuszob), utolso,
                self.JT_atlag(), self.JT_p95(), self.JT_elerhetoseg(), self.JT_slo(cel))
