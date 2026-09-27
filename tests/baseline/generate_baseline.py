"""Generate baseline hasil aplikasi Streamlit TQQ tanpa menjalankan UI."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from _app_logic import PROJECT_ROOT, load_app_logic


INPUT_DIR = PROJECT_ROOT / "tests" / "fixtures" / "input"
EXPECTED_DIR = PROJECT_ROOT / "tests" / "fixtures" / "expected"
PESERTA_FILE = INPUT_DIR / "peserta_testing.xlsx"
NILAI_FILE = INPUT_DIR / "nilai_testing.xlsx"


def ensure_input_fixtures() -> None:
    """Buat fixture Excel terpisah bila project belum menyediakannya.

    Data ini sengaja hanya ada di tests/fixtures/input dan mencakup data valid,
    nilai kosong, nama berbeda, NIM duplikat, nilai tidak valid, serta NIM nilai
    yang tidak ada pada peserta. Tidak pernah dipakai aplikasi production.
    """
    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not PESERTA_FILE.exists():
        peserta = pd.DataFrame([
            ["Alya Putri", "P", "240001", "1A", "Teknik Informatika"],
            ["Bagas Pratama", "L", "240002", "1A", "Teknik Informatika"],
            ["Citra Lestari", "P", "240003", "2B", "Sistem Informasi"],
            ["Deni Saputra", "L", "240004", "2B", "Sistem Informasi"],
            ["Eka Wulandari", "P", "240005", "10A", "Manajemen"],
            ["Fajar Nugroho", "L", "240006", "10A", "Manajemen"],
            ["Fajar Nugroho Duplikat", "L", "240006", "10A", "Manajemen"],
        ], columns=["Nama", "Jenis Kelamin", "NIM", "Kelas PAI", "Program Studi"])
        peserta.to_excel(PESERTA_FILE, index=False)

    if not NILAI_FILE.exists():
        nilai = pd.DataFrame([
            ["Alya Putri", "240001", "90", "88", "87", "92", "89", "A"],
            ["Bagas Pratama", "240002", "", "", "", "", "", ""],
            ["Siti Rahma", "240003", "105", "80", "85", "90", "90", "A"],
            ["Deni Saputra", "240004", "65", "70", "75", "80", "72", "C"],
            ["Deni Saputra", "240004", "75", "80", "85", "90", "82", "B"],
            ["Eka Wulandari", "240005", "90", "90", "90", "90", "N/A", "B"],
            ["Peserta Tidak Terdaftar", "249999", "80", "80", "80", "80", "80", "B"],
        ], columns=["NAMA", "NIM", "PRESENSI", "BACAAN", "HAFALAN", "EVALUASI", "TOTAL NILAI", "ABJAD"])
        nilai.to_excel(NILAI_FILE, index=False)


def load_results() -> dict[str, pd.DataFrame]:
    app = load_app_logic()
    raw_peserta = pd.read_excel(PESERTA_FILE, dtype=str)
    raw_nilai = pd.read_excel(NILAI_FILE, dtype=str)
    peserta, missing_peserta = app.standardize_dataframe(raw_peserta, app.PESERTA_COLUMN_ALIASES, "peserta")
    nilai, missing_nilai = app.standardize_dataframe(raw_nilai, app.NILAI_COLUMN_ALIASES, "nilai")
    if missing_peserta or missing_nilai:
        raise ValueError(
            "Kolom fixture tidak sesuai: "
            f"peserta={missing_peserta}, nilai={missing_nilai}"
        )
    return app.process_rekap(peserta, nilai)


def make_summary(results: dict[str, pd.DataFrame]) -> dict[str, Any]:
    total = len(results["rekap"])
    selesai = len(results["sudah_ada_nilai"])
    return {
        "total_peserta": total,
        "sudah_ada_nilai": selesai,
        "belum_ada_nilai": len(results["belum_ada_nilai"]),
        "perlu_dicek": len(results["perlu_dicek"]),
        "persentase_selesai": (selesai / total * 100) if total else 0,
    }


def save_dataframe(df: pd.DataFrame, path: Path) -> None:
    """Simpan representasi pembanding; index bukan bagian dari business logic."""
    df.reset_index(drop=True).to_csv(path, index=False, na_rep="")


def main() -> int:
    ensure_input_fixtures()
    EXPECTED_DIR.mkdir(parents=True, exist_ok=True)
    results = load_results()
    app = load_app_logic()

    (EXPECTED_DIR / "summary.json").write_text(
        json.dumps(make_summary(results), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    save_dataframe(results["rekap"], EXPECTED_DIR / "hasil_rekap.csv")
    save_dataframe(results["data_bermasalah"], EXPECTED_DIR / "data_bermasalah.csv")
    save_dataframe(results["ringkasan"], EXPECTED_DIR / "ringkasan_kelas.csv")
    save_dataframe(results["masalah_ringkasan"], EXPECTED_DIR / "ringkasan_masalah.csv")

    (EXPECTED_DIR / "export_final.xlsx").write_bytes(app.export_excel(results, include_per_kelas=True))
    (EXPECTED_DIR / "export_validasi.xlsx").write_bytes(app.export_laporan_validasi_excel(results))
    (EXPECTED_DIR / "export_data_bermasalah.xlsx").write_bytes(app.export_data_bermasalah_excel(results))

    print(f"Baseline dibuat dari: {PESERTA_FILE.relative_to(PROJECT_ROOT)}")
    print(f"Baseline dibuat dari: {NILAI_FILE.relative_to(PROJECT_ROOT)}")
    print(f"Output baseline disimpan di: {EXPECTED_DIR.relative_to(PROJECT_ROOT)}")
    print(json.dumps(make_summary(results), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
