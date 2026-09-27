"""Logic validasi rekap TQQ tanpa ketergantungan UI."""

import re
from typing import Any, Dict, List

import pandas as pd

from backend.app.core.config import PROBLEM_TYPE_ORDER, SCORE_RANGE_CONFIG
from backend.app.utils.helpers import is_blank, normalize_text


def parse_score(value: Any) -> float | None:
    """Mengubah nilai Excel menjadi angka. Mengembalikan None jika kosong/tidak valid."""
    if is_blank(value):
        return None
    text = str(value).strip()
    text = text.replace(",", ".")
    text = re.sub(r"[^0-9.\-]", "", text)
    if text in {"", ".", "-", "-."}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def score_range_issue(value: Any, minimum: float, maximum: float) -> str:
    """Mengembalikan pesan masalah jika nilai tidak angka atau di luar rentang."""
    if is_blank(value):
        return ""
    number = parse_score(value)
    if number is None:
        return "bukan angka"
    if number < minimum or number > maximum:
        return f"di luar rentang {minimum:g}-{maximum:g}"
    return ""


def get_score_range_notes(row: pd.Series) -> List[str]:
    notes: List[str] = []
    for col, config in SCORE_RANGE_CONFIG.items():
        issue = score_range_issue(row.get(col, ""), config["min"], config["max"])
        if issue:
            notes.append(f"{config['label']} {issue}")
    return notes


def add_problem(
    problems: List[Dict[str, Any]], sumber: str, jenis: str, nim: Any = "", nama_peserta: Any = "",
    nama_nilai: Any = "", kode_kelas_pai: Any = "", jenis_kelamin: Any = "", keterangan: str = "",
    kolom: str = "", nilai_terdeteksi: Any = "",
):
    problems.append({
        "Sumber": sumber, "Jenis Masalah": jenis, "NIM": normalize_text(nim),
        "Nama File Peserta": normalize_text(nama_peserta), "Nama File Nilai": normalize_text(nama_nilai),
        "Kode Kelas PAI": normalize_text(kode_kelas_pai), "Jenis Kelamin": normalize_text(jenis_kelamin),
        "Kolom": normalize_text(kolom), "Nilai Terdeteksi": normalize_text(nilai_terdeteksi),
        "Keterangan": keterangan,
    })


def build_problem_table(
    peserta_df: pd.DataFrame, nilai_df: pd.DataFrame, rekap: pd.DataFrame, unmatched_nilai: pd.DataFrame,
) -> pd.DataFrame:
    """Membuat daftar masalah utama sesuai kebutuhan panitia."""
    problems: List[Dict[str, Any]] = []

    for _, row in unmatched_nilai.iterrows():
        add_problem(problems, "File Nilai", "NIM di file nilai tidak ada di file peserta", row.get("nim", ""), "", row.get("nama_nilai", ""), "", "", "Ada nilai untuk NIM ini, tetapi NIM tidak ditemukan di file peserta.")

    for _, row in rekap[rekap["abjad"].apply(is_blank)].iterrows():
        add_problem(problems, "File Nilai", "Abjad kosong", row.get("nim", ""), row.get("nama", ""), row.get("nama_nilai", ""), row.get("kode_kelas_pai", ""), row.get("jenis_kelamin", ""), "Kolom ABJAD kosong atau peserta belum ditemukan di file nilai.")

    for _, row in rekap[rekap["total_nilai"].apply(is_blank)].iterrows():
        add_problem(problems, "File Nilai", "Total Nilai kosong", row.get("nim", ""), row.get("nama", ""), row.get("nama_nilai", ""), row.get("kode_kelas_pai", ""), row.get("jenis_kelamin", ""), "Kolom TOTAL NILAI kosong atau peserta belum ditemukan di file nilai.")

    for _, row in rekap[rekap["nama_berbeda"].fillna(False)].iterrows():
        add_problem(problems, "Gabungan Peserta + Nilai", "Nama berbeda antara file peserta dan file nilai", row.get("nim", ""), row.get("nama", ""), row.get("nama_nilai", ""), row.get("kode_kelas_pai", ""), row.get("jenis_kelamin", ""), f"Kemiripan nama sekitar {row.get('kemiripan_nama', 0):.0%}. Perlu dicek manual.")

    duplicate_nilai = nilai_df[nilai_df["nim"].ne("") & nilai_df["nim"].duplicated(keep=False)]
    for _, row in duplicate_nilai.iterrows():
        add_problem(problems, "File Nilai", "NIM duplikat di file nilai", row.get("nim", ""), "", row.get("nama_nilai", ""), "", "", "NIM muncul lebih dari sekali di file nilai. Sistem memakai data terakhir saat rekap.")

    for _, row in rekap.iterrows():
        for col, config in SCORE_RANGE_CONFIG.items():
            issue = score_range_issue(row.get(col, ""), config["min"], config["max"])
            if issue:
                add_problem(problems, "File Nilai", "Nilai tidak valid atau di luar rentang", row.get("nim", ""), row.get("nama", ""), row.get("nama_nilai", ""), row.get("kode_kelas_pai", ""), row.get("jenis_kelamin", ""), f"Kolom {config['label']} bernilai '{normalize_text(row.get(col, ''))}' dan {issue}. Rentang yang diterima: {config['min']:g}-{config['max']:g}.", kolom=config["label"], nilai_terdeteksi=row.get(col, ""))

    columns = ["Sumber", "Jenis Masalah", "NIM", "Nama File Peserta", "Nama File Nilai", "Kode Kelas PAI", "Jenis Kelamin", "Kolom", "Nilai Terdeteksi", "Keterangan"]
    if not problems:
        return pd.DataFrame(columns=columns)

    result = pd.DataFrame(problems, columns=columns)
    result["_urutan_masalah"] = result["Jenis Masalah"].apply(lambda value: PROBLEM_TYPE_ORDER.index(value) if value in PROBLEM_TYPE_ORDER else 999)
    result = result.sort_values(by=["_urutan_masalah", "Kode Kelas PAI", "NIM", "Nama File Peserta", "Nama File Nilai"], ascending=True, na_position="last").drop(columns=["_urutan_masalah"])
    return result
