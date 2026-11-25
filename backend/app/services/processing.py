"""Proses pembacaan, standardisasi, dan rekap TQQ tanpa ketergantungan UI."""

from typing import Dict, List, Tuple

import pandas as pd

from backend.app.core.config import (
    FINAL_COLUMN_LABELS,
    PROBLEM_TYPE_ORDER,
)
from backend.app.services.validation import build_problem_table
from backend.app.utils.prodi import canonical_prodi_map
from backend.app.utils.helpers import (
    detect_column_mapping,
    is_blank,
    name_similarity,
    natural_sort_kelas_key,
    normalize_gender,
    normalize_header,
    normalize_kelas_for_compare,
    normalize_name_for_compare,
    normalize_nim,
    normalize_text,
)


def canonical_to_required_label(canonical_name: str, file_type: str) -> str:
    if file_type == "peserta":
        return FINAL_COLUMN_LABELS.get(canonical_name, canonical_name)
    label_map = {
        "nama_nilai": "NAMA",
        "nim": "NIM",
        "kode_kelas_pai_nilai": "KODE KELAS PAI",
        "prodi_nilai": "PROGRAM STUDI",
        "presensi": "PRESENSI",
        "bacaan": "BACAAN",
        "hafalan": "HAFALAN",
        "evaluasi": "EVALUASI",
        "total_nilai": "TOTAL NILAI",
        "abjad": "ABJAD",
    }
    return label_map.get(canonical_name, canonical_name)


def standardize_dataframe(df: pd.DataFrame, aliases: Dict[str, List[str]], file_type: str) -> Tuple[pd.DataFrame, List[str]]:
    mapping, missing = detect_column_mapping(df, aliases)
    if missing:
        missing_labels = [canonical_to_required_label(col, file_type) for col in missing]
        return pd.DataFrame(), missing_labels

    standardized = pd.DataFrame()
    for canonical, original_col in mapping.items():
        standardized[canonical] = df[original_col]

    if "nim" in standardized.columns:
        standardized["nim"] = standardized["nim"].apply(normalize_nim)
        standardized = standardized[
            ~standardized["nim"].apply(lambda x: normalize_header(x) in {"nim", "npm", "no induk", "nomor induk"})
        ].copy()

    for col in standardized.columns:
        if col != "nim":
            standardized[col] = standardized[col].apply(lambda x: "" if pd.isna(x) else str(x).strip())

    return standardized, []


def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    filename = uploaded_file.name.lower()
    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file, dtype=str)
    if filename.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file, dtype=str)
    raise ValueError("Format file tidak didukung. Gunakan .xlsx, .xls, atau .csv")


def process_rekap(peserta_df: pd.DataFrame, nilai_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    peserta_clean = peserta_df.dropna(how="all").copy()
    nilai_clean = nilai_df.dropna(how="all").copy()

    for col in ("kode_kelas_pai_nilai", "prodi_nilai"):
        if col not in nilai_clean.columns:
            nilai_clean[col] = ""
        else:
            nilai_clean[col] = nilai_clean[col].apply(normalize_text)

    peserta_clean["nim"] = peserta_clean["nim"].apply(normalize_nim)
    nilai_clean["nim"] = nilai_clean["nim"].apply(normalize_nim)
    if "jenis_kelamin" in peserta_clean.columns:
        peserta_clean["jenis_kelamin"] = peserta_clean["jenis_kelamin"].apply(normalize_gender)

    prodi_map = canonical_prodi_map(
        list(peserta_clean["prodi"]) + list(nilai_clean["prodi_nilai"])
    )
    peserta_clean["prodi"] = peserta_clean["prodi"].apply(
        lambda value: prodi_map.get(normalize_text(value), normalize_text(value))
    )

    peserta_for_merge = peserta_clean[peserta_clean["nim"].ne("")].copy()
    nilai_for_merge = nilai_clean[nilai_clean["nim"].ne("")].copy()

    peserta_unique = peserta_for_merge.drop_duplicates(subset=["nim"], keep="first").copy()
    master_names = peserta_unique.set_index("nim")["nama"].to_dict()
    nilai_for_merge["_source_order"] = range(len(nilai_for_merge))
    nilai_for_merge["_name_match"] = nilai_for_merge.apply(
        lambda row: int(
            normalize_name_for_compare(row.get("nama_nilai", ""))
            == normalize_name_for_compare(master_names.get(row["nim"], ""))
            and not is_blank(row.get("nama_nilai", ""))
        ),
        axis=1,
    )
    score_columns = ["presensi", "bacaan", "hafalan", "evaluasi", "total_nilai", "abjad"]
    nilai_for_merge["_score_completeness"] = nilai_for_merge.apply(
        lambda row: (
            int(not is_blank(row.get("total_nilai", ""))) * 10
            + int(not is_blank(row.get("abjad", ""))) * 10
            + sum(not is_blank(row.get(col, "")) for col in score_columns)
        ),
        axis=1,
    )
    nilai_unique = (
        nilai_for_merge.sort_values(
            by=["nim", "_name_match", "_score_completeness", "_source_order"],
            kind="stable",
        )
        .drop_duplicates(subset=["nim"], keep="last")
        .drop(columns=["_source_order", "_name_match", "_score_completeness"])
        .copy()
    )

    unmatched_nilai = nilai_unique[~nilai_unique["nim"].isin(peserta_unique["nim"])].copy()
    rekap = peserta_unique.merge(nilai_unique, on="nim", how="left", suffixes=("", "_nilai_file"))

    rekap["status_nilai"] = rekap.apply(
        lambda row: "Sudah Ada Nilai" if any(not is_blank(row.get(col, "")) for col in score_columns) else "Belum Ada Nilai",
        axis=1,
    )
    rekap["kemiripan_nama"] = rekap.apply(
        lambda row: name_similarity(row.get("nama", ""), row.get("nama_nilai", ""))
        if not is_blank(row.get("nama_nilai", "")) else 1.0,
        axis=1,
    )
    rekap["nama_berbeda"] = rekap.apply(
        lambda row: (not is_blank(row.get("nama", "")))
        and (not is_blank(row.get("nama_nilai", "")))
        and normalize_name_for_compare(row.get("nama", ""))
        != normalize_name_for_compare(row.get("nama_nilai", "")),
        axis=1,
    )
    rekap["kelas_berbeda"] = rekap.apply(
        lambda row: (
            not is_blank(row.get("kode_kelas_pai", ""))
            and not is_blank(row.get("kode_kelas_pai_nilai", ""))
            and normalize_kelas_for_compare(row.get("kode_kelas_pai", ""))
            != normalize_kelas_for_compare(row.get("kode_kelas_pai_nilai", ""))
        ),
        axis=1,
    )
    rekap["prodi_berbeda"] = rekap.apply(
        lambda row: (
            not is_blank(row.get("prodi", ""))
            and not is_blank(row.get("prodi_nilai", ""))
            and normalize_name_for_compare(row.get("prodi", ""))
            != normalize_name_for_compare(prodi_map.get(normalize_text(row.get("prodi_nilai", "")), row.get("prodi_nilai", "")))
        ),
        axis=1,
    )

    sort_keys = rekap["kode_kelas_pai"].apply(natural_sort_kelas_key)
    rekap["_sort_angka"] = sort_keys.apply(lambda x: x[0])
    rekap["_sort_huruf"] = sort_keys.apply(lambda x: x[1])
    rekap["_sort_asli"] = sort_keys.apply(lambda x: x[2])
    rekap = rekap.sort_values(by=["_sort_angka", "_sort_huruf", "_sort_asli", "nama"], ascending=True, na_position="last").drop(columns=["_sort_angka", "_sort_huruf", "_sort_asli"])

    data_bermasalah = build_problem_table(peserta_clean, nilai_clean, rekap, unmatched_nilai)
    notes_by_nim: dict[str, list[str]] = {}
    for _, problem in data_bermasalah.iterrows():
        nim = problem["NIM"]
        if not nim:
            continue
        note = problem["Jenis Masalah"]
        if note in {"Komponen nilai kosong", "Nilai tidak valid atau di luar rentang", "Data identitas kosong di file nilai"}:
            note += f" ({problem['Kolom']})"
        notes = notes_by_nim.setdefault(nim, [])
        if note not in notes:
            notes.append(note)
    rekap["catatan_validasi"] = rekap["nim"].apply(
        lambda nim: "; ".join(notes_by_nim.get(nim, [])) or "-"
    )
    rekap["status_validasi"] = rekap["catatan_validasi"].apply(
        lambda note: "Valid" if note == "-" else "Perlu Dicek"
    )

    sudah_ada_nilai = rekap[rekap["status_nilai"] == "Sudah Ada Nilai"].copy()
    belum_ada_nilai = rekap[rekap["status_nilai"] == "Belum Ada Nilai"].copy()
    perlu_dicek = rekap[rekap["status_validasi"] == "Perlu Dicek"].copy()

    ringkasan = rekap.groupby("kode_kelas_pai", dropna=False).agg(
        total_peserta=("nim", "count"),
        sudah_ada_nilai=("status_nilai", lambda x: (x == "Sudah Ada Nilai").sum()),
        belum_ada_nilai=("status_nilai", lambda x: (x == "Belum Ada Nilai").sum()),
        perlu_dicek=("status_validasi", lambda x: (x == "Perlu Dicek").sum()),
    ).reset_index()

    if not ringkasan.empty:
        ringkasan["persentase_selesai"] = ringkasan.apply(lambda row: (row["sudah_ada_nilai"] / row["total_peserta"] * 100) if row["total_peserta"] else 0, axis=1)
        sort_keys_ringkasan = ringkasan["kode_kelas_pai"].apply(natural_sort_kelas_key)
        ringkasan["_sort_angka"] = sort_keys_ringkasan.apply(lambda x: x[0])
        ringkasan["_sort_huruf"] = sort_keys_ringkasan.apply(lambda x: x[1])
        ringkasan["_sort_asli"] = sort_keys_ringkasan.apply(lambda x: x[2])
        ringkasan = ringkasan.sort_values(by=["_sort_angka", "_sort_huruf", "_sort_asli"]).drop(columns=["_sort_angka", "_sort_huruf", "_sort_asli"])

    ringkasan = ringkasan.rename(columns={
        "kode_kelas_pai": "Kode Kelas PAI", "total_peserta": "Total Peserta",
        "sudah_ada_nilai": "Sudah Ada Nilai", "belum_ada_nilai": "Belum Ada Nilai",
        "perlu_dicek": "Perlu Dicek", "persentase_selesai": "Persentase Selesai (%)",
    })

    masalah_ringkasan = data_bermasalah["Jenis Masalah"].value_counts().reset_index() if not data_bermasalah.empty else pd.DataFrame(columns=["Jenis Masalah", "Jumlah"])
    if not masalah_ringkasan.empty:
        masalah_ringkasan.columns = ["Jenis Masalah", "Jumlah"]
        masalah_ringkasan["_urutan_masalah"] = masalah_ringkasan["Jenis Masalah"].apply(lambda value: PROBLEM_TYPE_ORDER.index(value) if value in PROBLEM_TYPE_ORDER else 999)
        masalah_ringkasan = masalah_ringkasan.sort_values(by=["_urutan_masalah", "Jenis Masalah"], ascending=True).drop(columns=["_urutan_masalah"])

    return {
        "rekap": rekap, "sudah_ada_nilai": sudah_ada_nilai, "belum_ada_nilai": belum_ada_nilai,
        "perlu_dicek": perlu_dicek, "ringkasan": ringkasan, "data_bermasalah": data_bermasalah,
        "masalah_ringkasan": masalah_ringkasan, "unmatched_nilai": unmatched_nilai,
    }
