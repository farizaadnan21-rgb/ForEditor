# ForEditor

**ForEditor** adalah aplikasi editor gambar desktop ringan berbasis Python dan Tkinter. Dirancang untuk portfolio developer: antarmuka gelap modern, alat menggambar intuitif, penyesuaian gambar real-time, dan efek spesial yang bisa di-toggle — tanpa membebani mesin seperti software editing profesional penuh.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-2c3e50)
![OpenCV](https://img.shields.io/badge/OpenCV-image%20processing-5C3EE8)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Fitur utama

| Kategori | Fitur |
|----------|--------|
| **Menggambar** | Kuas bulat, kotak, spray · penghapus · pilih warna · ukuran kuas (1–50) |
| **Penyesuaian** | Kecerahan, kontras, saturasi, temperatur warna (biru ↔ kuning), denoise — preview langsung via slider |
| **Efek spesial** | Sketsa pensil, cyberpunk neon, sepia vintage — toggle on/off (klik 2× untuk nonaktif) |
| **Produktivitas** | Undo / Redo (20 langkah) · Load / Save (PNG) · Reset kanvas |
| **UI** | Tema dark modern · sidebar ber-scroll · status bar · highlight tool aktif |

---

## Cuplikan antarmuka

> Tambahkan screenshot aplikasi di folder `docs/` (mis. `docs/screenshot.png`) lalu sisipkan di sini:
>
> `![ForEditor screenshot](docs/screenshot.png)`

---

## Persyaratan sistem

- **Python** 3.10 atau lebih baru  
- **Tkinter** (biasanya sudah termasuk instalasi Python di Linux/Windows/macOS)  
- Dependensi Python: lihat [`requirements.txt`](requirements.txt)

---

## Instalasi

```bash
# Clone repository
git clone https://github.com/<username>/ForEditor.git
cd ForEditor

# (Opsional) virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Install dependensi
pip install -r requirements.txt
```

---

## Menjalankan aplikasi

```bash
python3 ForEditor.py
```

### Pintasan keyboard

| Pintasan | Aksi |
|----------|------|
| `Ctrl + Z` | Undo |
| `Ctrl + Y` | Redo |

---

## Deploy ke Vercel (landing page)

Repository ini berisi **dua bagian**:

| Bagian | File | Di mana berjalan |
|--------|------|------------------|
| **Situs web portfolio** | `public/index.html` | Vercel (browser) |
| **Aplikasi editor** | `ForEditor.py` | Komputer lokal (Python + Tkinter) |

Vercel **tidak bisa** menjalankan GUI Tkinter di browser. Setelah push, Vercel menampilkan halaman statis di `public/` — bukan error 404.

```bash
# Uji lokal sebelum deploy
npm run dev
# Buka http://localhost:3000
```

Push ke GitHub → Vercel redeploy otomatis. Pastikan **Root Directory** di Vercel = root repo (bukan subfolder kosong).

---

## Struktur proyek

```
ForEditor/
├── ForEditor.py          # Aplikasi desktop (GUI + logika editing)
├── public/               # Situs statis untuk Vercel
│   ├── index.html
│   └── css/style.css
├── vercel.json           # Konfigurasi output: public/
├── package.json
├── requirements.txt      # Dependensi Python (desktop)
├── README.md
├── FOR_EDITOR/           # Versi modular (referensi)
├── konsep.sln            # Eksperimen C# terpisah
└── ...
```

> **Catatan:** Editor dijalankan dengan **`python3 ForEditor.py`**. Website Vercel hanya dokumentasi/portfolio.

---

## Stack teknologi

- **[Tkinter](https://docs.python.org/3/library/tkinter.html)** — antarmuka grafis desktop  
- **[Pillow (PIL)](https://python-pillow.org/)** — manipulasi gambar, layer menggambar  
- **[OpenCV](https://opencv.org/)** — filter, efek, denoise, temperatur warna  
- **[NumPy](https://numpy.org/)** — operasi matriks untuk efek lanjutan  

---

## Alur kerja singkat

1. **Gambar** di kanvas putih atau **Load** gambar dari file.  
2. Atur kuas / penghapus di sidebar kiri.  
3. Buka accordion **Penyesuaian Gambar** untuk slider live preview.  
4. Terapkan **Efek Spesial**; klik lagi efek yang sama untuk menonaktifkan.  
5. **Save** hasil sebagai PNG.

Efek spesial yang masih aktif akan “dikunci” ke gambar saat Anda mulai menggambar lagi (sesuai desain toggle).

---

## Kontribusi

Issue dan pull request dipersilakan. Untuk perubahan besar, buka issue terlebih dahulu agar align dengan arah proyek.

---

## Lisensi

Proyek ini menggunakan lisensi **MIT** — bebas digunakan, dimodifikasi, dan didistribusikan dengan atribusi. (Tambahkan file `LICENSE` jika belum ada.)

---

## Author

Dibuat sebagai proyek portfolio — **ForEditor** · lightweight image editor.
