"""Konfigurasi dan konstanta yang digunakan oleh business logic TQQ."""

import os

APP_TITLE = "Rekap Nilai TQQ Akbar UNESA"
MODE_REKAP = "Mode Rekap Peserta & Nilai"
MODE_RAPIKAN = "Mode Rapikan Hasil Rekap"


def _parse_cors_origins(value: str) -> list[str]:
    """Parse origin CORS comma-separated dari environment deployment."""
    return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]


CORS_ORIGINS = _parse_cors_origins(
    os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
)

PESERTA_REQUIRED_COLUMNS = [
    "Nama", "Jenis Kelamin", "NIM", "Kelas PAI", "Program Studi",
]

NILAI_REQUIRED_COLUMNS = [
    "NAMA", "NIM", "PRESENSI", "BACAAN", "HAFALAN", "EVALUASI", "TOTAL NILAI", "ABJAD",
]

PESERTA_COLUMN_ALIASES = {
    "nama": ["Nama", "NAMA", "nama"],
    "jenis_kelamin": [
        "Jenis Kelamin", "JENIS KELAMIN", "jenis kelamin", "Gender", "GENDER",
        "L/P", "JK",
    ],
    "nim": ["NIM", "Nim", "nim", "NPM", "npm", "No Induk", "Nomor Induk"],
    "prodi": ["Prodi", "PRODI", "prodi", "Program Studi", "PROGRAM STUDI", "program studi"],
    "kode_kelas_pai": [
        "Kode Kelas PAI", "KODE KELAS PAI", "kode kelas pai", "Kelas PAI", "KELAS PAI",
        "kelas pai", "Kode PAI", "KODE PAI", "kode pai",
    ],
}

NILAI_COLUMN_ALIASES = {
    "nama_nilai": ["NAMA", "Nama", "nama"],
    "nim": ["NIM", "Nim", "nim", "NPM", "npm"],
    "presensi": ["PRESENSI", "Presensi", "presensi", "Presensi Kehadiran"],
    "bacaan": ["BACAAN", "Bacaan", "bacaan"],
    "hafalan": ["HAFALAN", "Hafalan", "hafalan"],
    "evaluasi": ["EVALUASI", "Evaluasi", "evaluasi"],
    "total_nilai": [
        "TOTAL NILAI", "Total Nilai", "total nilai", "TOTAL_NILAI", "total_nilai",
        "TOTAL", "Total", "total",
    ],
    "abjad": ["ABJAD", "Abjad", "abjad", "Huruf", "HURUF", "huruf"],
}

REKAP_COLUMN_ALIASES = {
    "nim": ["NIM", "Nim", "nim", "NPM", "npm", "No Induk", "Nomor Induk"],
    "prodi": ["Prodi", "PRODI", "prodi", "Program Studi", "PROGRAM STUDI", "program studi"],
    "kode_kelas_pai": [
        "Kode Kelas PAI", "KODE KELAS PAI", "kode kelas pai", "Kelas PAI", "KELAS PAI",
        "kelas pai", "Kode PAI", "KODE PAI", "kode pai",
    ],
}

REKAP_REQUIRED_COLUMN_LABELS = {"nim": "NIM", "prodi": "Prodi", "kode_kelas_pai": "Kode Kelas PAI"}
REKAP_INTERNAL_COLUMNS = {
    "nim": "__rekap_nim", "prodi": "__rekap_prodi", "kode_kelas_pai": "__rekap_kode_kelas_pai",
}

FINAL_COLUMNS = [
    "nama", "jenis_kelamin", "nim", "prodi", "kode_kelas_pai",
    "nama_nilai", "presensi", "bacaan", "hafalan", "evaluasi", "total_nilai", "abjad",
    "status_nilai", "status_validasi", "catatan_validasi",
]

FINAL_COLUMN_LABELS = {
    "nama": "Nama", "jenis_kelamin": "Jenis Kelamin", "nim": "NIM", "prodi": "Prodi",
    "kode_kelas_pai": "Kode Kelas PAI",
    "nama_nilai": "Nama dari File Nilai", "presensi": "Presensi", "bacaan": "Bacaan",
    "hafalan": "Hafalan", "evaluasi": "Evaluasi", "total_nilai": "Total Nilai", "abjad": "Abjad",
    "status_nilai": "Status Nilai", "status_validasi": "Status Validasi",
    "catatan_validasi": "Catatan Validasi",
}

EXPORT_PER_KELAS_COLUMNS = [
    "nama", "jenis_kelamin", "nim", "prodi", "kode_kelas_pai",
    "presensi", "bacaan", "hafalan", "evaluasi", "total_nilai", "abjad",
]

EXPORT_PER_KELAS_COLUMN_LABELS = {
    "nama": "Nama", "jenis_kelamin": "Jenis Kelamin", "nim": "NIM", "prodi": "Prodi",
    "kode_kelas_pai": "Kode Kelas PAI",
    "presensi": "PRESENSI", "bacaan": "BACAAN", "hafalan": "HAFALAN",
    "evaluasi": "EVALUASI", "total_nilai": "TOTAL NILAI", "abjad": "ABJAD",
}

PROBLEM_TYPE_ORDER = [
    "NIM di file nilai tidak ada di file peserta", "Abjad kosong", "Total Nilai kosong",
    "Nama berbeda antara file peserta dan file nilai", "NIM duplikat di file nilai",
    "Nilai tidak valid atau di luar rentang",
]

SCORE_RANGE_CONFIG = {
    "presensi": {"label": "PRESENSI", "min": 0, "max": 100},
    "bacaan": {"label": "BACAAN", "min": 0, "max": 100},
    "hafalan": {"label": "HAFALAN", "min": 0, "max": 100},
    "evaluasi": {"label": "EVALUASI", "min": 0, "max": 100},
    "total_nilai": {"label": "TOTAL NILAI", "min": 0, "max": 100},
}

# --- Konfigurasi mode Rekap Pembagian Kelas Jilid ---

MASTER_REQUIRED_COLUMN_LABELS = {
    "nama": "Nama", "jenis_kelamin": "Jenis Kelamin", "nim": "NIM",
    "kode_kelas_pai": "Kelas PAI", "prodi": "Program Studi",
}

PENILAIAN_TASHIH_COLUMN_ALIASES = {
    "nama_nilai": ["NAMA", "Nama", "nama"],
    "nim": ["NIM", "Nim", "nim", "NPM", "npm"],
    "prodi_nilai": ["PRODI", "Prodi", "prodi", "Program Studi", "PROGRAM STUDI"],
    "total_nilai": [
        "Total", "TOTAL", "Total Nilai", "TOTAL NILAI", "total", "total nilai",
    ],
}

PENILAIAN_TASHIH_REQUIRED_COLUMN_LABELS = {"nim": "NIM", "total_nilai": "Total Nilai"}

JILID_TOTAL_RANGE = {"min": 0, "max": 100}

JILID_LABELS = ["Jilid 1", "Jilid 2", "Jilid 3", "Jilid 4"]

JILID_GENDER_SHEET_LABELS = [("L", "Laki-laki"), ("P", "Perempuan")]

JILID_OUTPUT_COLUMNS = ["nama", "jenis_kelamin", "nim", "kode_kelas_pai", "prodi"]

JILID_OUTPUT_COLUMN_LABELS = {
    "nama": "Nama", "jenis_kelamin": "Jenis Kelamin", "nim": "NIM",
    "kode_kelas_pai": "Kelas PAI", "prodi": "Program Studi",
}


def jilid_sheet_name(jilid_label: str, gender_label: str) -> str:
    """Nama sheet Excel untuk kombinasi Jilid + Jenis Kelamin pada hasil Rekap Jilid.

    Dipakai bersama oleh export (``jilid_service``) dan pembacaan ulang file hasil
    Rekap Jilid (``tentor_service``) agar penamaan sheet selalu konsisten.
    """
    return f"{jilid_label} - {gender_label}"[:31]


# --- Konfigurasi mode Pembagian Tentor ---

TENTOR_OUTPUT_COLUMNS = list(JILID_OUTPUT_COLUMN_LABELS.values())
