# Cover Auto

Aplikasi web desktop lokal untuk membuat template cover hardcover massal dari banyak file PDF.

Fitur utama:

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
├── pyproject.toml
└── README.md
```

## Instalasi

Python yang ditargetkan adalah Python 3.14.

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Jika Python 3.14 belum tersedia, versi Python modern yang kompatibel dengan dependensi FastAPI juga dapat digunakan untuk pengembangan.

## Menjalankan Aplikasi

```bash
uvicorn app.main:app --reload
```

Buka browser ke:

```text
http://127.0.0.1:8000
```

## Cara Pakai

1. Upload banyak file PDF.
2. Atur lebar punggung sesuai tebal buku.
3. Atur gap punggung ke cover depan bila diperlukan; default 5 mm.
4. Klik **Generate Cover**.
5. Download ZIP hasil generate.
6. Buka file `cover_auto_multipage.svg` di CorelDRAW 17, cek tiap page/group, lalu simpan sebagai `.cdr`.

## Output

Setiap proses membuat folder timestamp di `output/` berisi:

- `cover_auto_multipage.svg`: satu file SVG berisi semua cover sebagai group page.
- `page_001_*.svg`, `page_002_*.svg`, dst.: file SVG per PDF.
- `preview.html`: preview semua hasil di browser.
- `cover_auto_output.zip`: paket ZIP hasil generate.
