# Rekap Nilai TQQ Akbar UNESA

Aplikasi rekap nilai TQQ Akbar UNESA menggunakan frontend Next.js dan backend
FastAPI. Setelah mengunggah file master peserta dan file nilai, pengguna
memilih rekap berdasarkan Prodi atau Kode Kelas PAI. Excel final berisi satu
sheet per kelompok yang dipilih, dengan peserta diurutkan berdasarkan NIM.
Variasi penulisan nama Prodi yang sangat mirip disatukan dalam jenjang yang
sama; Prodi S1 dan D4 tetap dibuat pada sheet terpisah.
Data Bermasalah mencocokkan NIM dengan master sebagai acuan identitas. Baris
nilai dengan NIM berbeda, NIM duplikat, kolom identitas kosong, komponen nilai
kosong, dan nilai di luar rentang dilaporkan terpisah agar mudah diperbaiki.

## Prasyarat

- Python 3.12+
- Node.js 20+

## Backend FastAPI

Instal dependency dan jalankan untuk development:

```powershell
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

API tersedia di `http://localhost:8000` dan Swagger di
`http://localhost:8000/docs`.

### Environment backend

Salin `backend/.env.example` sebagai referensi konfigurasi deployment. Sistem
deployment harus menyediakan environment variable berikut:

```text
CORS_ORIGINS=https://app.example.com
```

Untuk development, default CORS mengizinkan `http://localhost:3000` dan
`http://127.0.0.1:3000`. Pada production, gunakan origin frontend publik yang
spesifik dan dipisahkan koma bila lebih dari satu.

Jalankan production server, misalnya:

```powershell
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
```

> Hasil rekap saat ini menggunakan session sementara di memori.
> Untuk deployment saat ini gunakan satu worker/backend instance atau sticky
> routing. Penyimpanan persisten dapat ditambahkan pada tahap terpisah.

## Frontend Next.js

```powershell
cd frontend
Copy-Item .env.example .env.local
npm ci
npm run dev
```

Untuk localhost atau berbagi lewat satu tunnel ngrok, kosongkan
`NEXT_PUBLIC_API_URL` dan arahkan `BACKEND_API_URL` ke backend lokal
(`http://127.0.0.1:8000`). Next.js meneruskan permintaan `/api/*` ke backend,
sehingga browser pengguna mengakses frontend dan API melalui domain yang sama.
Jalankan backend di port 8000, frontend di port 3000, lalu arahkan ngrok ke
port 3000. Periksa `https://<domain-ngrok>/api/health`; hasil yang benar ialah
`{"status":"ok"}`. Mulai ulang Next.js setelah mengubah `.env.local`.
Untuk deployment dengan API publik terpisah, isi `NEXT_PUBLIC_API_URL` dengan
URL API publik sebelum build frontend.

### Production build frontend

```powershell
cd frontend
npm ci
npm run build
npm run start
```

## Verifikasi

```powershell
python tests/baseline/verify_baseline.py
python tests/baseline/verify_fastapi_integration.py
cd frontend
npm run build
```

Antarmuka sebelum migrasi disimpan sebagai arsip di `legacy/` dan tidak
digunakan oleh aplikasi utama.
