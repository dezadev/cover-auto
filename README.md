# Cover Auto

Aplikasi web desktop lokal untuk membuat template cover hardcover massal dari banyak file PDF.

## Cara Paling Mudah Menjalankan

### Windows

1. Install Python dari <https://www.python.org/downloads/>.
2. Saat install Python, centang **Add Python to PATH**.
3. Klik dua kali file:

```text
mulai_windows.bat
```

Launcher akan otomatis:

- membuat folder `.venv`,
- menginstall dependency,
- menjalankan server lokal,
- membuka browser ke `http://127.0.0.1:8000`.

### Linux / macOS

Jalankan:

```bash
./mulai_linux_mac.sh
```

Atau:

```bash
python3 run_app.py
```

## Jika Launcher Otomatis Gagal

Gunakan langkah manual berikut dari folder project:

```bash
python -m venv .venv
```

Windows:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Linux / macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Kemudian buka:

```text
http://127.0.0.1:8000
```

## Fitur Utama

- Area kerja A3+ berukuran 297 x 430 mm.
- Lebar punggung buku dapat diatur manual per batch.
- Jarak/gap antara punggung dan cover depan 5 mm secara default.
- Area cover depan dibuat sebagai bingkai presisi dengan tautan ke PDF sumber untuk proses place/import di CorelDRAW.
- Teks punggung diekstrak otomatis dari PDF sebagai judul awal.
- Banyak PDF dapat digenerate menjadi satu dokumen SVG multi-page; setiap PDF menjadi satu page/layer group.
- Tersedia file HTML preview per halaman dan paket ZIP output.

> Catatan CorelDRAW 17: format `.cdr` bersifat proprietary dan tidak dapat dibuat langsung secara native dari Python tanpa CorelDRAW/Windows COM automation. Aplikasi ini menghasilkan SVG berukuran presisi dalam mm yang dapat dibuka/import di CorelDRAW 17, lalu disimpan sebagai `.cdr`.

## Struktur Folder

```text
cover-auto/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point aplikasi web
│   ├── cover_generator.py   # Logika ekstraksi PDF dan generate SVG/HTML
│   ├── models.py            # Model konfigurasi layout
│   ├── static/
│   │   └── styles.css
│   └── templates/
│       ├── index.html
│       └── result.html
├── input_pdfs/              # Letakkan file PDF sumber di sini bila ingin memakai folder input
├── output/                  # Hasil generate disimpan di sini
├── mulai_windows.bat        # Klik dua kali di Windows
├── mulai_linux_mac.sh       # Launcher Linux/macOS
├── run_app.py               # Launcher Python otomatis
├── requirements.txt         # Daftar dependency untuk pip
├── pyproject.toml
└── README.md
```

## Cara Pakai Aplikasi

1. Jalankan aplikasi memakai `mulai_windows.bat`, `./mulai_linux_mac.sh`, atau `python3 run_app.py`.
2. Upload banyak file PDF.
3. Atur lebar punggung sesuai tebal buku.
4. Atur gap punggung ke cover depan bila diperlukan; default 5 mm.
5. Klik **Generate Cover**.
6. Download ZIP hasil generate.
7. Buka file `cover_auto_multipage.svg` di CorelDRAW 17, cek tiap page/group, lalu simpan sebagai `.cdr`.

## Output

Setiap proses membuat folder timestamp di `output/` berisi:

- `cover_auto_multipage.svg`: satu file SVG berisi semua cover sebagai group page.
- `page_001_*.svg`, `page_002_*.svg`, dst.: file SVG per PDF.
- `preview.html`: preview semua hasil di browser.
- `cover_auto_output.zip`: paket ZIP hasil generate.
