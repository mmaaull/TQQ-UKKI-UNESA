# Rekap Nilai TQQ Akbar UNESA

Aplikasi rekap nilai TQQ Akbar UNESA menggunakan frontend Next.js dan backend
FastAPI. Logic rekap, validasi, export Excel, dan mode rapikan berada pada
service backend serta dijaga oleh baseline test.

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

> Hasil rekap dan rapikan saat ini menggunakan session sementara di memori.
> Untuk deployment saat ini gunakan satu worker/backend instance atau sticky
> routing. Penyimpanan persisten dapat ditambahkan pada tahap terpisah.

## Frontend Next.js

```powershell
cd frontend
Copy-Item .env.example .env.local
npm ci
npm run dev
```

Set `NEXT_PUBLIC_API_URL` di `frontend/.env.local` ke URL FastAPI, misalnya
`http://localhost:8000` untuk development atau `https://api.example.com`
untuk production. Nilai ini dibaca ketika build frontend.

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
