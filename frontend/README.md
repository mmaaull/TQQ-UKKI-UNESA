# Frontend Rekap Nilai TQQ

Frontend production menggunakan Next.js. URL backend berasal dari
`NEXT_PUBLIC_API_URL` pada environment build.

## Development

```powershell
Copy-Item .env.example .env.local
npm ci
npm run dev
```

Atur `NEXT_PUBLIC_API_URL=http://localhost:8000` untuk backend lokal.

## Production

Sediakan `NEXT_PUBLIC_API_URL` dengan URL API publik sebelum build, misalnya
`https://api.example.com`.

```powershell
npm ci
npm run build
npm run start
```

Nilai `NEXT_PUBLIC_*` dibaca saat build; lakukan build ulang bila URL API
berubah.
