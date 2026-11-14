import heapq
import random
import time
import tkinter as tk
from collections import deque
from tkinter import ttk


class LabirentAjanUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("YZT - Labirentte Yol Bulan Ajan (Hibrit BFS & A* Karşılaştırması)")
        self.root.configure(bg="#12161f")
        self.root.resizable(False, False)

        # Şartname: En az 20x50 karelik grid (21 satır x 51 sütun)
        self.satir = 21
        self.sutun = 51
        self.hucre_boyutu = 20

        self.baslangic = (10, 2)
        self.hedef = (10, 48)
        self.ajan_konum = self.baslangic
        self.labirent = []
        self.animasyon_aktif = False
        self.son_cizilen_hucre = None

        self.renkler = {
            "duvar": "#1e2533",
            "yol": "#f8fafc",
            "baslangic": "#10b981",
            "hedef": "#ef4444",
            "ziyaret": "#93c5fd",
            "en_kisa_yol": "#f59e0b",
            "ajan": "#7c3aed",
        }

        self._arayuz_olustur()
        self.engel_parkuru_uret()

    def _arayuz_olustur(self):
        ust_panel = tk.Frame(self.root, bg="#12161f", pady=8, padx=14)
        ust_panel.pack(fill="x")

        tk.Label(
            ust_panel,
            text="Labirentte Yol Bulan Yapay Zeka Ajanı (21x51 Grid)",
            font=("Segoe UI", 13, "bold"),
            fg="#f8fafc",
            bg="#12161f",
        ).pack(side="left")

        kontrol_panel = tk.Frame(self.root, bg="#181e2a", pady=8, padx=14)
        kontrol_panel.pack(fill="x", padx=14, pady=(0, 8))

        tk.Label(kontrol_panel, text="Mod:", fg="#cbd5e1", bg="#181e2a", font=("Segoe UI", 9, "bold")).pack(side="left", padx=(0, 5))
        self.algoritma_secimi = ttk.Combobox(
            kontrol_panel,
            values=[
                "Hibrit (BFS + Dinamik Engel)",
                "A* (A-Star)",
                "BFS (Genislik Oncelikli)",
                "Q-Learning (Pekistirmeli)",
            ],
            state="readonly",
            width=26,
            font=("Segoe UI", 9),
        )
        self.algoritma_secimi.current(0)
        self.algoritma_secimi.pack(side="left", padx=(0, 10))

        tk.Label(kontrol_panel, text="Hız:", fg="#cbd5e1", bg="#181e2a", font=("Segoe UI", 9)).pack(side="left", padx=(0, 3))
        self.hiz_olcegi = tk.Scale(
            kontrol_panel,
            from_=1,
            to=30,
            orient="horizontal",
            bg="#181e2a",
            fg="#f8fafc",
            highlightthickness=0,
            length=85,
        )
        self.hiz_olcegi.set(6)
        self.hiz_olcegi.pack(side="left", padx=(0, 10))

        self.baslat_btn = tk.Button(
            kontrol_panel,
            text="▶ Ajanı Başlat",
            command=self.ajani_baslat,
            bg="#2563eb",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
        )
        self.baslat_btn.pack(side="left", padx=3)

        self.karsilastir_btn = tk.Button(
            kontrol_panel,
            text="⚖️ BFS vs A* Karşılaştır",
            command=self.bfs_astar_karsilastir,
            bg="#7c3aed",
            fg="white",
            font=("Segoe UI", 9, "bold"),
            relief="flat",
            padx=10,
            pady=4,
            cursor="hand2",
        )
        self.karsilastir_btn.pack(side="left", padx=3)

        tk.Button(
            kontrol_panel,
            text="🧱 Engel Parkuru (18+ Engel)",
            command=self.engel_parkuru_uret,
            bg="#334155",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=9,
            pady=4,
            cursor="hand2",
        ).pack(side="left", padx=3)

        tk.Button(
            kontrol_panel,
            text="↻ Labirent Üret",
            command=self.yeni_labirent_uret,
            bg="#334155",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=9,
            pady=4,
            cursor="hand2",
        ).pack(side="left", padx=3)

        tk.Button(
            kontrol_panel,
            text="🧹 Temizle",
            command=self.yolu_temizle,
            bg="#475569",
            fg="white",
            font=("Segoe UI", 9),
            relief="flat",
            padx=9,
            pady=4,
            cursor="hand2",
        ).pack(side="left", padx=3)

        govde = tk.Frame(self.root, bg="#12161f", padx=14, pady=4)
        govde.pack()

        genislik = self.sutun * self.hucre_boyutu
        yukseklik = self.satir * self.hucre_boyutu
        self.canvas = tk.Canvas(
            govde,
            width=genislik,
            height=yukseklik,
            bg="#1e2533",
            highlightthickness=2,
            highlightbackground="#334155",
        )
        self.canvas.pack(side="left")

        # Sol tık / sürükle: Duvar ekle | Sağ tık / sürükle: Duvar sil
        self.canvas.bind("<Button-1>", lambda e: self.fare_duvar_islem(e, 1))
        self.canvas.bind("<B1-Motion>", lambda e: self.fare_duvar_islem(e, 1))
        self.canvas.bind("<Button-3>", lambda e: self.fare_duvar_islem(e, 0))
        self.canvas.bind("<B3-Motion>", lambda e: self.fare_duvar_islem(e, 0))

        sag_panel = tk.Frame(govde, bg="#181e2a", width=285, height=yukseklik, padx=12, pady=10)
        sag_panel.pack(side="left", fill="y", padx=(12, 0))
        sag_panel.pack_propagate(False)

        tk.Label(sag_panel, text="📊 Aktif Çalışma Metrikleri", font=("Segoe UI", 10, "bold"), fg="#f8fafc", bg="#181e2a").pack(anchor="w")
        self.durum_etiketi = tk.Label(
            sag_panel,
            text="Durum: Hazır",
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg="#181e2a",
            justify="left",
            wraplength=260,
        )
        self.durum_etiketi.pack(anchor="w", pady=(3, 5))

        self.metrik_etiketi = tk.Label(
            sag_panel,
            text="Algoritma: -\nBakılan Kare Sayısı: 0\nYol Uzunluğu: 0 adım\nSüre: 0.00 ms | Dinamik Rota: 0",
            font=("Consolas", 9),
            fg="#e2e8f0",
            bg="#0f172a",
            justify="left",
            padx=8,
            pady=7,
        )
        self.metrik_etiketi.pack(fill="x", pady=(0, 8))

        tk.Label(sag_panel, text="⚖️ Bonus: BFS vs A* Karşılaştırma", font=("Segoe UI", 10, "bold"), fg="#c4b5fd", bg="#181e2a").pack(anchor="w")
        self.karsilastirma_etiketi = tk.Label(
            sag_panel,
            text="Metrik        |  BFS   |   A*\n"
                 "--------------+--------+--------\n"
                 "Bakılan Kare  |   -    |   -\n"
                 "Yol Adımı     |   -    |   -\n"
                 "Süre (ms)     |   -    |   -\n"
                 "Tarama Farkı  | -",
            font=("Consolas", 8),
            fg="#f1f5f9",
            bg="#0f172a",
            justify="left",
            padx=8,
            pady=7,
        )
        self.karsilastirma_etiketi.pack(fill="x", pady=(4, 8))

        aciklamalar = [
            ("Başlangıç", "#10b981"),
            ("Hedef", "#ef4444"),
            ("Taranan Kare", "#93c5fd"),
            ("En Kısa Yol", "#f59e0b"),
            ("Ajan", "#7c3aed"),
        ]
        renk_satiri = tk.Frame(sag_panel, bg="#181e2a")
        renk_satiri.pack(anchor="w", pady=2)
        for metin, renk in aciklamalar[:3]:
            tk.Label(renk_satiri, bg=renk, width=2).pack(side="left", padx=(0, 3))
            tk.Label(renk_satiri, text=metin, fg="#cbd5e1", bg="#181e2a", font=("Segoe UI", 8)).pack(side="left", padx=(0, 8))

        renk_satiri2 = tk.Frame(sag_panel, bg="#181e2a")
        renk_satiri2.pack(anchor="w", pady=2)
        for metin, renk in aciklamalar[3:]:
            tk.Label(renk_satiri2, bg=renk, width=2).pack(side="left", padx=(0, 3))
            tk.Label(renk_satiri2, text=metin, fg="#cbd5e1", bg="#181e2a", font=("Segoe UI", 8)).pack(side="left", padx=(0, 8))

        tk.Label(
            sag_panel,
            text="Sol Tık/Sürükle: Duvar Ekle | Sağ Tık: Sil\n(Ajan yürürken önüne duvar koyabilirsiniz)",
            font=("Segoe UI", 8, "italic"),
            fg="#94a3b8",
            bg="#181e2a",
            justify="left",
        ).pack(side="bottom", anchor="w")

    def _sinirlari_hazirla(self):
        self.labirent = [[0 for _ in range(self.sutun)] for _ in range(self.satir)]
        for r in range(self.satir):
            self.labirent[r][0] = 1
            self.labirent[r][self.sutun - 1] = 1
        for c in range(self.sutun):
            self.labirent[0][c] = 1
            self.labirent[self.satir - 1][c] = 1

    def engel_parkuru_uret(self):
        if self.animasyon_aktif:
            return
        self._sinirlari_hazirla()
        # Minimum 8 engelden kaçma şartı için 18+ çok hücreli engel bloğu yerleştir
        engel_sayisi = 0
        deneme = 0
        while engel_sayisi < 20 and deneme < 300:
            deneme += 1
            r = random.randint(2, self.satir - 5)
            c = random.randint(5, self.sutun - 6)
            dikey = random.choice([True, False])
            uzunluk = random.randint(3, 5)
            hucreler = [(r + i, c) if dikey else (r, c + i) for i in range(uzunluk)]

            if any(h in (self.baslangic, self.hedef) for h in hucreler):
                continue
            for hr, hc in hucreler:
                self.labirent[hr][hc] = 1

            # Yolun tamamen kapanmadığını BFS ile doğrula
            _, test_yol = self.bfs_coz(self.baslangic)
            if test_yol:
                engel_sayisi += 1
            else:
                for hr, hc in hucreler:
                    self.labirent[hr][hc] = 0

        self.ajan_konum = self.baslangic
        self.labirenti_ciz()
        self.durum_etiketi.config(text=f"Durum: {engel_sayisi} engelli 21x51 parkur hazır.", fg="#38bdf8")

    def yeni_labirent_uret(self):
        if self.animasyon_aktif:
            return
        self.labirent = [[1 for _ in range(self.sutun)] for _ in range(self.satir)]

        def kaz(r, c):
            self.labirent[r][c] = 0
            yonler = [(0, 2), (0, -2), (2, 0), (-2, 0)]
            random.shuffle(yonler)
            for dr, dc in yonler:
                nr, nc = r + dr, c + dc
                if 1 <= nr < self.satir - 1 and 1 <= nc < self.sutun - 1 and self.labirent[nr][nc] == 1:
                    self.labirent[r + dr // 2][c + dc // 2] = 0
                    kaz(nr, nc)

        kaz(1, 1)
        # Alternatif kısa yollar oluşması için ara duvarların bir kısmını aç
        for _ in range(45):
            rr = random.randint(2, self.satir - 3)
            cc = random.randint(2, self.sutun - 3)
            self.labirent[rr][cc] = 0

        self.labirent[self.baslangic[0]][self.baslangic[1]] = 0
        self.labirent[self.hedef[0]][self.hedef[1]] = 0
        self.ajan_konum = self.baslangic
        self.labirenti_ciz()
        self.durum_etiketi.config(text="Durum: Yeni 21x51 labirent üretildi.", fg="#38bdf8")

    def yolu_temizle(self):
        if self.animasyon_aktif:
            return
        self.ajan_konum = self.baslangic
        self.labirenti_ciz()
        self.durum_etiketi.config(text="Durum: Harita temizlendi.", fg="#38bdf8")

    def fare_duvar_islem(self, event, deger):
        c = event.x // self.hucre_boyutu
        r = event.y // self.hucre_boyutu
        if not (0 <= r < self.satir and 0 <= c < self.sutun):
            return
        if (r, c) in (self.baslangic, self.hedef, self.ajan_konum):
            return
        if self.labirent[r][c] != deger:
            self.labirent[r][c] = deger
            self.hucre_boya(r, c, self.renkler["duvar"] if deger == 1 else self.renkler["yol"])

    def hucre_boya(self, r, c, renk):
        x1 = c * self.hucre_boyutu
        y1 = r * self.hucre_boyutu
        x2 = x1 + self.hucre_boyutu
        y2 = y1 + self.hucre_boyutu
        kenar = "#e2e8f0" if renk != self.renkler["duvar"] else "#1e2533"
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=renk, outline=kenar)

    def labirenti_ciz(self):
        self.canvas.delete("all")
        for r in range(self.satir):
            for c in range(self.sutun):
                renk = self.renkler["duvar"] if self.labirent[r][c] == 1 else self.renkler["yol"]
                self.hucre_boya(r, c, renk)
        self.hucre_boya(*self.baslangic, self.renkler["baslangic"])
        self.hucre_boya(*self.hedef, self.renkler["hedef"])

    def komsular(self, nokta):
        r, c = nokta
        sonuc = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.satir and 0 <= nc < self.sutun and self.labirent[nr][nc] == 0:
                sonuc.append((nr, nc))
        return sonuc

    def bfs_coz(self, baslangic=None):
        bas = baslangic or self.baslangic
        kuyruk = deque([bas])
        ebeveyn = {bas: None}
        ziyaret_sirasi = []

        while kuyruk:
            mevcut = kuyruk.popleft()
            ziyaret_sirasi.append(mevcut)
            if mevcut == self.hedef:
                break
            for komsu in self.komsular(mevcut):
                if komsu not in ebeveyn:
                    ebeveyn[komsu] = mevcut
                    kuyruk.append(komsu)

        return ziyaret_sirasi, self._yolu_cikar(ebeveyn)

    def astar_coz(self, baslangic=None):
        bas = baslangic or self.baslangic

        def manhattan(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        acik_kume = [(0, bas)]
        ebeveyn = {bas: None}
        g_skoru = {bas: 0}
        ziyaret_sirasi = []

        while acik_kume:
            _, mevcut = heapq.heappop(acik_kume)
            if mevcut in ziyaret_sirasi:
                continue
            ziyaret_sirasi.append(mevcut)
            if mevcut == self.hedef:
                break

            for komsu in self.komsular(mevcut):
                yeni_g = g_skoru[mevcut] + 1
                if komsu not in g_skoru or yeni_g < g_skoru[komsu]:
                    g_skoru[komsu] = yeni_g
                    f_skoru = yeni_g + manhattan(komsu, self.hedef)
                    ebeveyn[komsu] = mevcut
                    heapq.heappush(acik_kume, (f_skoru, komsu))

        return ziyaret_sirasi, self._yolu_cikar(ebeveyn)

    def q_learning_coz(self):
        aksiyonlar = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        q_tablosu = {}
        alfa, gama, epsilon = 0.25, 0.95, 0.35
        ziyaret_edilenler = set()

        for _ in range(1400):
            durum = self.baslangic
            for _ in range(600):
                ziyaret_edilenler.add(durum)
                if durum == self.hedef:
                    break
                if random.random() < epsilon:
                    a_idx = random.randint(0, 3)
                else:
                    q_degerleri = [q_tablosu.get((durum, i), 0.0) for i in range(4)]
                    max_q = max(q_degerleri)
                    a_idx = random.choice([i for i, q in enumerate(q_degerleri) if q == max_q])

                nr, nc = durum[0] + aksiyonlar[a_idx][0], durum[1] + aksiyonlar[a_idx][1]
                if 0 <= nr < self.satir and 0 <= nc < self.sutun and self.labirent[nr][nc] == 0:
                    yeni_durum = (nr, nc)
                    odul = 100.0 if yeni_durum == self.hedef else -0.2
                else:
                    yeni_durum = durum
                    odul = -5.0

                eski_q = q_tablosu.get((durum, a_idx), 0.0)
                sonraki_max = max([q_tablosu.get((yeni_durum, i), 0.0) for i in range(4)])
                q_tablosu[(durum, a_idx)] = eski_q + alfa * (odul + gama * sonraki_max - eski_q)
                durum = yeni_durum

        yol = [self.baslangic]
        mevcut = self.baslangic
        gorulen = {mevcut}
        for _ in range(self.satir * self.sutun):
            if mevcut == self.hedef:
                break
            q_degerleri = [q_tablosu.get((mevcut, i), -999.0) for i in range(4)]
            a_idx = q_degerleri.index(max(q_degerleri))
            nr, nc = mevcut[0] + aksiyonlar[a_idx][0], mevcut[1] + aksiyonlar[a_idx][1]
            if (nr, nc) in gorulen or not (0 <= nr < self.satir and 0 <= nc < self.sutun) or self.labirent[nr][nc] == 1:
                break
            mevcut = (nr, nc)
            gorulen.add(mevcut)
            yol.append(mevcut)

        if yol[-1] != self.hedef:
            yol = []
        return list(ziyaret_edilenler), yol

    def _yolu_cikar(self, ebeveyn):
        if self.hedef not in ebeveyn:
            return []
        yol = []
        mevcut = self.hedef
        while mevcut is not None:
            yol.append(mevcut)
            mevcut = ebeveyn[mevcut]
        yol.reverse()
        return yol

    def bfs_astar_karsilastir(self):
        if self.animasyon_aktif:
            return
        self.labirenti_ciz()

        t0 = time.perf_counter()
        bfs_ziyaret, bfs_yol = self.bfs_coz(self.baslangic)
        bfs_ms = (time.perf_counter() - t0) * 1000

        t1 = time.perf_counter()
        astar_ziyaret, astar_yol = self.astar_coz(self.baslangic)
        astar_ms = (time.perf_counter() - t1) * 1000

        if not bfs_yol or not astar_yol:
            self.durum_etiketi.config(text="Durum: Hedefe ulaşan yol yok!", fg="#ef4444")
            return

        tasarruf = ((len(bfs_ziyaret) - len(astar_ziyaret)) / max(1, len(bfs_ziyaret))) * 100
        self.karsilastirma_etiketi.config(
            text=f"Metrik        |  BFS   |   A*\n"
                 f"--------------+--------+--------\n"
                 f"Bakılan Kare  | {len(bfs_ziyaret):^6} | {len(astar_ziyaret):^6}\n"
                 f"Yol Adımı     | {len(bfs_yol)-1:^6} | {len(astar_yol)-1:^6}\n"
                 f"Süre (ms)     | {bfs_ms:^6.2f} | {astar_ms:^6.2f}\n"
                 f"A* Verimi     | %{tasarruf:.1f} daha az kare"
        )

        self.animasyon_aktif = True
        self._buton_durumu("disabled")
        self.durum_etiketi.config(text="Durum: A* araması ve en kısa yol çiziliyor...", fg="#c4b5fd")
        self._animasyon_adimi(astar_ziyaret, astar_yol, 0, 0, "A* (Karşılaştırma)", astar_ms, len(astar_ziyaret), 0, False)

    def ajani_baslat(self):
        if self.animasyon_aktif:
            return
        self.ajan_konum = self.baslangic
        self.labirenti_ciz()
        secim = self.algoritma_secimi.get()
        hibrit_aktif = secim.startswith("Hibrit")

        t0 = time.perf_counter()
        if secim.startswith("A*"):
            ziyaret, yol = self.astar_coz(self.baslangic)
        elif secim.startswith("BFS") or hibrit_aktif:
            ziyaret, yol = self.bfs_coz(self.baslangic)
        else:
            ziyaret, yol = self.q_learning_coz()
        sure_ms = (time.perf_counter() - t0) * 1000

        self.animasyon_aktif = True
        self._buton_durumu("disabled")
        self.durum_etiketi.config(text=f"Durum: {secim.split()[0]} çalışıyor...", fg="#fbbf24")
        self._animasyon_adimi(ziyaret, yol, 0, 0, secim.split()[0], sure_ms, len(ziyaret), 0, hibrit_aktif)

    def _buton_durumu(self, durum):
        self.baslat_btn.config(state=durum)
        self.karsilastir_btn.config(state=durum)

    def _animasyon_adimi(self, ziyaret, yol, z_idx, y_idx, ad, sure_ms, toplam_ziyaret, dinamik_sayac, hibrit_aktif):
        gecikme = self.hiz_olcegi.get()

        # 1. Faz: Arama alanını boya
        if z_idx < len(ziyaret):
            nokta = ziyaret[z_idx]
            if nokta not in (self.baslangic, self.hedef) and self.labirent[nokta[0]][nokta[1]] == 0:
                self.hucre_boya(*nokta, self.renkler["ziyaret"])
            self.root.after(
                gecikme,
                self._animasyon_adimi,
                ziyaret,
                yol,
                z_idx + 1,
                y_idx,
                ad,
                sure_ms,
                toplam_ziyaret,
                dinamik_sayac,
                hibrit_aktif,
            )
            return

        # 2. Faz: Bulunan yolda ajanı yürüt (Hibrit modda önü kapanırsa dinamik rota yeniden hesapla)
        if y_idx < len(yol):
            if hibrit_aktif and any(self.labirent[r][c] == 1 for r, c in yol[y_idx:]):
                t_yeni = time.perf_counter()
                yeni_ziyaret, yeni_yol = self.bfs_coz(self.ajan_konum)
                sure_ms += (time.perf_counter() - t_yeni) * 1000
                toplam_ziyaret += len(yeni_ziyaret)
                dinamik_sayac += 1
                if not yeni_yol:
                    self.animasyon_aktif = False
                    self._buton_durumu("normal")
                    self.durum_etiketi.config(text="Durum: Yeni duvarlar yolu tamamen kapattı!", fg="#ef4444")
                    return
                for zr, zc in yeni_ziyaret:
                    if (zr, zc) not in (self.baslangic, self.hedef, self.ajan_konum) and self.labirent[zr][zc] == 0:
                        self.hucre_boya(zr, zc, "#bae6fd")
                yol = yeni_yol
                y_idx = 1 if len(yol) > 1 else 0
                self.durum_etiketi.config(text=f"Durum: Engel algılandı! Dinamik rota #{dinamik_sayac}", fg="#f97316")

            nokta = yol[y_idx]
            if self.ajan_konum not in (self.baslangic, self.hedef) and self.labirent[self.ajan_konum[0]][self.ajan_konum[1]] == 0:
                self.hucre_boya(*self.ajan_konum, self.renkler["en_kisa_yol"])
            self.ajan_konum = nokta
            if nokta not in (self.baslangic, self.hedef):
                self.hucre_boya(*nokta, self.renkler["ajan"])

            self.root.after(
                gecikme + 12,
                self._animasyon_adimi,
                ziyaret,
                yol,
                z_idx,
                y_idx + 1,
                ad,
                sure_ms,
                toplam_ziyaret,
                dinamik_sayac,
                hibrit_aktif,
            )
            return

        self.animasyon_aktif = False
        self._buton_durumu("normal")
        if yol:
            self.durum_etiketi.config(text="Durum: Hedefe başarıyla ulaşıldı!", fg="#10b981")
            self.metrik_etiketi.config(
                text=f"Algoritma: {ad}\n"
                     f"Bakılan Kare Sayısı: {toplam_ziyaret}\n"
                     f"Yol Uzunluğu: {len(yol) - 1} adım\n"
                     f"Süre: {sure_ms:.2f} ms | Dinamik Rota: {dinamik_sayac}"
            )
        else:
            self.durum_etiketi.config(text="Durum: Hedefe giden yol bulunamadı!", fg="#ef4444")


if __name__ == "__main__":
    pencere = tk.Tk()
    uygulama = LabirentAjanUygulamasi(pencere)
    pencere.mainloop()