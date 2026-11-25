# Frontend Rekap Nilai TQQ

Frontend menggunakan Next.js. Untuk localhost dan satu tunnel ngrok, permintaan
`/api/*` diteruskan oleh Next.js ke `BACKEND_API_URL`.

## Development

```powershell
Copy-Item .env.example .env.local
npm ci
npm run dev
```

Biarkan `NEXT_PUBLIC_API_URL` kosong dan atur
`BACKEND_API_URL=http://127.0.0.1:8000` untuk backend lokal. Jalankan ngrok ke
port frontend 3000 jika ingin berbagi aplikasi. Pastikan backend di port 8000
tetap berjalan dan `/api/health` pada domain ngrok mengembalikan `{"status":"ok"}`.

## Production

Jika API dipasang pada domain publik terpisah, isi `NEXT_PUBLIC_API_URL` dengan
URL API publik sebelum build, misalnya `https://api.example.com`.

```powershell
npm ci
npm run build
npm run start
```

Nilai `NEXT_PUBLIC_*` dibaca saat build; lakukan build ulang bila URL API
berubah.
