"""Logic validasi rekap TQQ tanpa ketergantungan UI."""

import re
from typing import Any, Dict, List

import pandas as pd

from backend.app.core.config import PROBLEM_TYPE_ORDER, SCORE_RANGE_CONFIG
from backend.app.utils.helpers import is_blank, normalize_name_for_compare, normalize_text


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
    prodi_peserta: Any = "", prodi_nilai: Any = "", kode_kelas_pai_nilai: Any = "",
):
    problems.append({
        "Sumber": sumber, "Jenis Masalah": jenis, "NIM": normalize_text(nim),
        "Nama File Peserta": normalize_text(nama_peserta), "Nama File Nilai": normalize_text(nama_nilai),
        "Kode Kelas PAI": normalize_text(kode_kelas_pai), "Jenis Kelamin": normalize_text(jenis_kelamin),
        "Prodi Master": normalize_text(prodi_peserta), "Prodi File Nilai": normalize_text(prodi_nilai),
        "Kode Kelas PAI File Nilai": normalize_text(kode_kelas_pai_nilai),
        "Kolom": normalize_text(kolom), "Nilai Terdeteksi": normalize_text(nilai_terdeteksi),
        "Keterangan": keterangan,
    })


def build_problem_table(
    peserta_df: pd.DataFrame, nilai_df: pd.DataFrame, rekap: pd.DataFrame, unmatched_nilai: pd.DataFrame,
) -> pd.DataFrame:
    """Bandingkan file nilai dengan identitas master dan nilai yang benar-benar dipakai."""
    problems: List[Dict[str, Any]] = []
    master_with_nim = peserta_df[peserta_df["nim"].ne("")]
    nilai_with_nim = nilai_df[nilai_df["nim"].ne("")]
    master_by_nim = master_with_nim.drop_duplicates("nim").set_index("nim")
    master_names: dict[str, list[str]] = {}
    for _, row in master_with_nim.iterrows():
        key = normalize_name_for_compare(row.get("nama", ""))
        if key:
            master_names.setdefault(key, []).append(row["nim"])

    def add_row_issue(row: pd.Series, sumber: str, jenis: str, keterangan: str, kolom: str = "", nilai_terdeteksi: Any = "") -> None:
        add_problem(
            problems, sumber, jenis, row.get("nim", ""), row.get("nama", ""),
            row.get("nama_nilai", ""), row.get("kode_kelas_pai", ""),
            row.get("jenis_kelamin", ""), keterangan, kolom, nilai_terdeteksi,
            row.get("prodi", ""), row.get("prodi_nilai", ""), row.get("kode_kelas_pai_nilai", ""),
        )

    for _, row in peserta_df[peserta_df["nim"].eq("")].iterrows():
        add_row_issue(row, "File Master", "NIM kosong di file master", "Baris master tidak dapat dicocokkan dengan file nilai.", "NIM")
    for _, row in nilai_df[nilai_df["nim"].eq("")].iterrows():
        add_row_issue(row, "File Nilai", "NIM kosong di file nilai", "Baris nilai tidak dapat dicocokkan dengan master.", "NIM")

    for nim, group in master_with_nim.groupby("nim", sort=False):
        if len(group) > 1:
            for position, (_, row) in enumerate(group.iterrows(), start=1):
                add_row_issue(row, "File Master", "NIM duplikat di file master", f"Baris {position} dari {len(group)} dengan NIM yang sama; rekap memakai baris pertama. Periksa nama dan identitas tiap baris.", "NIM", nim)
    for nim, group in nilai_with_nim.groupby("nim", sort=False):
        if len(group) > 1:
            master = master_by_nim.loc[nim] if nim in master_by_nim.index else None
            for position, (_, row) in enumerate(group.iterrows(), start=1):
                add_problem(
                    problems, "File Nilai", "NIM duplikat di file nilai", nim,
                    master.get("nama", "") if master is not None else "",
                    row.get("nama_nilai", ""),
                    master.get("kode_kelas_pai", "") if master is not None else "",
                    master.get("jenis_kelamin", "") if master is not None else "",
                    f"Baris {position} dari {len(group)} dengan NIM yang sama; rekap memilih nama yang cocok dengan master dan nilai paling lengkap.",
                    "NIM", nim,
                    master.get("prodi", "") if master is not None else "",
                    row.get("prodi_nilai", ""), row.get("kode_kelas_pai_nilai", ""),
                )

    for _, row in peserta_df.iterrows():
        for col, label in (("nama", "Nama"), ("prodi", "Program Studi"), ("kode_kelas_pai", "Kode Kelas PAI")):
            if is_blank(row.get(col, "")):
                add_row_issue(row, "File Master", "Data identitas kosong di file master", f"Kolom {label} di master kosong.", label)

    name_mismatch_nims: set[str] = set()
    for _, row in unmatched_nilai.iterrows():
        candidates = set(master_names.get(normalize_name_for_compare(row.get("nama_nilai", "")), []))
        if len(candidates) == 1:
            master_nim = next(iter(candidates))
            master = master_by_nim.loc[master_nim]
            name_mismatch_nims.add(master_nim)
            add_problem(
                problems, "Gabungan Peserta + Nilai", "NIM berbeda antara file master dan file nilai",
                master_nim, master.get("nama", ""), row.get("nama_nilai", ""),
                master.get("kode_kelas_pai", ""), master.get("jenis_kelamin", ""),
                f"Nama sama, tetapi NIM master '{master_nim}' dan NIM file nilai '{row['nim']}' berbeda. Nilai belum digabung sampai NIM diperbaiki.",
                "NIM", row["nim"], master.get("prodi", ""), row.get("prodi_nilai", ""), row.get("kode_kelas_pai_nilai", ""),
            )
        else:
            add_problem(
                problems, "File Nilai", "NIM di file nilai tidak ada di file peserta",
                row.get("nim", ""), "", row.get("nama_nilai", ""), "", "",
                "NIM file nilai tidak ditemukan di master; nama juga tidak cocok secara unik dengan master.",
                "NIM", row.get("nim", ""), "", row.get("prodi_nilai", ""), row.get("kode_kelas_pai_nilai", ""),
            )

    score_columns = ["presensi", "bacaan", "hafalan", "evaluasi", "total_nilai", "abjad"]
    matched_nims = set(nilai_with_nim["nim"]) & set(master_with_nim["nim"])
    for _, row in rekap.iterrows():
        nim = row["nim"]
        if nim not in matched_nims:
            if nim not in name_mismatch_nims:
                add_row_issue(row, "File Master", "Peserta belum ada di file nilai", "NIM master tidak ditemukan di file nilai.", "NIM", nim)
            continue

        for col, label in (("nama_nilai", "Nama"), ("kode_kelas_pai_nilai", "Kode Kelas PAI"), ("prodi_nilai", "Program Studi")):
            if is_blank(row.get(col, "")):
                add_row_issue(row, "File Nilai", "Data identitas kosong di file nilai", f"Kolom {label} di file nilai kosong; master tetap menjadi acuan.", label)

        if bool(row.get("nama_berbeda", False)):
            add_row_issue(row, "Gabungan Peserta + Nilai", "Nama berbeda antara file peserta dan file nilai", f"Nama master dan file nilai berbeda (kemiripan sekitar {row.get('kemiripan_nama', 0):.0%}). Periksa NIM dan ejaannya.", "NAMA", row.get("nama_nilai", ""))
        if bool(row.get("kelas_berbeda", False)):
            add_row_issue(row, "Gabungan Peserta + Nilai", "Kode Kelas PAI berbeda antara file peserta dan file nilai", "Kode kelas pada file nilai berbeda dari master.", "KODE KELAS PAI", row.get("kode_kelas_pai_nilai", ""))
        if bool(row.get("prodi_berbeda", False)):
            add_row_issue(row, "Gabungan Peserta + Nilai", "Program Studi berbeda antara file peserta dan file nilai", "Program Studi pada file nilai berbeda dari master.", "PROGRAM STUDI", row.get("prodi_nilai", ""))

        if all(is_blank(row.get(col, "")) for col in score_columns):
            add_row_issue(row, "File Nilai", "Nilai belum diisi", "Baris NIM ditemukan, tetapi seluruh kolom nilai dan ABJAD kosong.")
        else:
            for col, label in (("presensi", "PRESENSI"), ("bacaan", "BACAAN"), ("hafalan", "HAFALAN"), ("evaluasi", "EVALUASI")):
                if is_blank(row.get(col, "")):
                    add_row_issue(row, "File Nilai", "Komponen nilai kosong", f"Kolom {label} kosong pada baris nilai yang cocok dengan NIM master.", label)
            for col, label, jenis in (("total_nilai", "TOTAL NILAI", "Total Nilai kosong"), ("abjad", "ABJAD", "Abjad kosong")):
                if is_blank(row.get(col, "")):
                    add_row_issue(row, "File Nilai", jenis, f"Kolom {label} kosong pada baris nilai yang cocok dengan NIM master.", label)

        for col, config in SCORE_RANGE_CONFIG.items():
            issue = score_range_issue(row.get(col, ""), config["min"], config["max"])
            if issue:
                add_row_issue(row, "File Nilai", "Nilai tidak valid atau di luar rentang", f"Kolom {config['label']} bernilai '{normalize_text(row.get(col, ''))}' dan {issue}. Rentang yang diterima: {config['min']:g}-{config['max']:g}.", config["label"], row.get(col, ""))

    columns = [
        "Sumber", "Jenis Masalah", "NIM", "Nama File Peserta", "Nama File Nilai",
        "Kode Kelas PAI", "Kode Kelas PAI File Nilai", "Prodi Master", "Prodi File Nilai",
        "Jenis Kelamin", "Kolom", "Nilai Terdeteksi", "Keterangan",
    ]
    if not problems:
        return pd.DataFrame(columns=columns)

    result = pd.DataFrame(problems, columns=columns)
    result["_urutan_masalah"] = result["Jenis Masalah"].apply(lambda value: PROBLEM_TYPE_ORDER.index(value) if value in PROBLEM_TYPE_ORDER else 999)
    result = result.sort_values(by=["_urutan_masalah", "Kode Kelas PAI", "NIM", "Nama File Peserta", "Nama File Nilai"], ascending=True, na_position="last").drop(columns=["_urutan_masalah"])
    return result
