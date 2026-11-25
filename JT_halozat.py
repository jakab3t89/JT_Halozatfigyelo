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
        if ertek is not None and self.ip == "ismeretlen":
            self.ip = JT_feloldas(self.cim)
        if len(self.meresek) > 40:
            self.meresek.pop(0)

    def JT_sikeres(self):
        return [m for m in self.meresek if m is not None]

    def JT_atlag(self):
        sikeres = self.JT_sikeres()
        if not sikeres:
            return "-"
        return round(statistics.mean(sikeres), 1)

    def JT_elerhetoseg(self):
        if not self.meresek:
            return "-"
        return f"{round(len(self.JT_sikeres()) / len(self.meresek) * 100)}%"

    def JT_allapot(self):
        if not self.meresek:
            return "várakozik"
        return "elérhető" if self.meresek[-1] is not None else "nem elérhető"

    def JT_sor(self):
        utolso = self.meresek[-1] if self.meresek and self.meresek[-1] is not None else "-"
        return (self.cim, self.port, self.ip, self.JT_allapot(), utolso, self.JT_atlag(), self.JT_elerhetoseg())
