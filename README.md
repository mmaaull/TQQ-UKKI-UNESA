# Rekap Nilai TQQ Akbar UNESA - Streamlit Web Dashboard Solid Blue

Aplikasi web dashboard sederhana untuk membantu panitia TQQ Akbar UNESA melakukan rekap nilai peserta berdasarkan **Kode Kelas PAI**.

## Teknologi

- Python
- Streamlit
- Pandas
- OpenPyXL
- Plotly

## Fitur Utama

- Upload File Peserta dan File Nilai
- Rekap berdasarkan NIM
- Validasi data otomatis
- Dashboard ringkasan
- Grafik status nilai, progress per kelas, kelas prioritas, dan jenis masalah
- Tampilan bernuansa biru solid tanpa gradient
- Panduan penggunaan berbentuk list
- Filter hasil rekap
- Export 1 file Excel dengan banyak sheet per Kode Kelas PAI

## Kolom File Peserta

- Nama
- NIM
- Prodi
- Kelas Umum
- Kode Kelas PAI
- Dosen Pengampu

## Kolom File Nilai

- NAMA
- NIM
- PRESENSI
- BACAAN
- HAFALAN
- EVALUASI
- TOTAL NILAI
- ABJAD

## Cara Menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Update v12

Jenis deteksi masalah pada menu validasi kini dibatasi menjadi:

1. NIM di file nilai tidak ada di file peserta
2. Abjad kosong
3. Total Nilai kosong
4. Nama berbeda antara file peserta dan file nilai
5. NIM duplikat di file nilai

Validasi `Dosen Pengampu kosong` sudah dihapus dari daftar masalah.

## Update v13

Tambahan fitur quality check:

1. **Cek rentang nilai**
   - PRESENSI, BACAAN, HAFALAN, EVALUASI, dan TOTAL NILAI dicek dengan rentang default 0–100.
   - Nilai yang bukan angka atau di luar rentang akan masuk ke Data Bermasalah.

2. **Preview hasil per Kode Kelas PAI sebelum export**
   - Menampilkan daftar sheet yang akan dibuat.
   - Menampilkan jumlah peserta, sudah ada nilai, belum ada nilai, dan perlu dicek per sheet.

3. **Download laporan validasi**
   - Berisi ringkasan validasi, ringkasan masalah, preview sheet export, aturan rentang nilai, semua masalah, peserta perlu dicek, dan sheet detail per jenis masalah.
