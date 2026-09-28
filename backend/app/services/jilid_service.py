"""Logic mode Rekap Pembagian Kelas Jilid tanpa ketergantungan UI.

File master (data keseluruhan peserta) menjadi acuan Nama, Jenis Kelamin,
Kelas PAI, dan Program Studi karena file penilaian tashih tidak memiliki
kolom jenis kelamin. Kelas Jilid dihitung ulang oleh sistem dari Total Nilai
di file penilaian (bukan dari kolom Jilid manual bila ada), lalu hasilnya
dipisah per Jilid (1-4) dan per jenis kelamin.
"""

from io import BytesIO
from typing import Any, Dict, List, Tuple

import pandas as pd

from backend.app.core.config import (
    JILID_GENDER_SHEET_LABELS,
    JILID_LABELS,
    JILID_OUTPUT_COLUMN_LABELS,
    JILID_OUTPUT_COLUMNS,
    JILID_TOTAL_RANGE,
    MASTER_REQUIRED_COLUMN_LABELS,
    PENILAIAN_TASHIH_COLUMN_ALIASES,
    PENILAIAN_TASHIH_REQUIRED_COLUMN_LABELS,
    PESERTA_COLUMN_ALIASES,
    jilid_sheet_name,
)
from backend.app.services.validation import parse_score
from backend.app.utils.helpers import (
    detect_column_mapping,
    is_blank,
    natural_sort_kelas_key,
    normalize_gender,
    normalize_header,
    normalize_nim,
    normalize_text,
    read_all_sheets,
)

MASTER_CANONICAL_COLUMNS = ["nama", "jenis_kelamin", "nim", "kode_kelas_pai", "prodi"]
HEADER_SCAN_LIMIT = 30


class MasterRequiredColumnError(ValueError):
    """Error ketika file master tidak memiliki kolom wajib."""


class PenilaianRequiredColumnError(ValueError):
    """Error ketika file penilaian tashih tidak memiliki kolom wajib."""


def read_master_file(uploaded_file) -> pd.DataFrame:
    """Baca seluruh sheet file master (biasanya per fakultas) dan gabungkan."""
    combined = read_all_sheets(uploaded_file)
    if combined.empty:
        return pd.DataFrame(columns=MASTER_CANONICAL_COLUMNS)

    mapping, missing = detect_column_mapping(combined, PESERTA_COLUMN_ALIASES)
    missing_required = [col for col in MASTER_CANONICAL_COLUMNS if col in missing]
    if missing_required:
        labels = [MASTER_REQUIRED_COLUMN_LABELS[col] for col in missing_required]
        raise MasterRequiredColumnError(
            "File master belum memiliki kolom: " + ", ".join(labels)
        )

    result = pd.DataFrame()
    for canonical in MASTER_CANONICAL_COLUMNS:
        result[canonical] = combined[mapping[canonical]]

    result["nim"] = result["nim"].apply(normalize_nim)
    result["jenis_kelamin"] = result["jenis_kelamin"].apply(normalize_gender)
    for col in ("nama", "kode_kelas_pai", "prodi"):
        result[col] = result[col].apply(normalize_text)

    result = result[result["nim"].ne("")].drop_duplicates(subset=["nim"], keep="first")
    return result.reset_index(drop=True)


def _find_header_row(raw: pd.DataFrame) -> int | None:
    """Cari baris header asli di file penilaian tashih (ada judul/instruksi di atasnya).

    Hanya kolom NIM yang dijadikan penanda karena kolom Nama bersifat opsional
    (lihat ``PENILAIAN_TASHIH_REQUIRED_COLUMN_LABELS``); mewajibkan Nama di sini
    membuat file tanpa kolom Nama gagal terbaca sama sekali.
    """
    max_scan = min(len(raw), HEADER_SCAN_LIMIT)
    for idx in range(max_scan):
        row_values = {normalize_header(value) for value in raw.iloc[idx].tolist()}
        if "nim" in row_values:
            return idx
    return None


def _extract_penilaian_sheet(raw: pd.DataFrame) -> pd.DataFrame | None:
    header_idx = _find_header_row(raw)
    if header_idx is None:
        return None

    body = raw.iloc[header_idx + 1 :].copy()
    body.columns = raw.iloc[header_idx].tolist()

    mapping, missing = detect_column_mapping(body, PENILAIAN_TASHIH_COLUMN_ALIASES)
    missing_required = [col for col in PENILAIAN_TASHIH_REQUIRED_COLUMN_LABELS if col in missing]
    if missing_required:
        labels = [PENILAIAN_TASHIH_REQUIRED_COLUMN_LABELS[col] for col in missing_required]
        raise PenilaianRequiredColumnError(
            "File penilaian belum memiliki kolom: " + ", ".join(labels)
        )

    result = pd.DataFrame()
    for canonical, original_col in mapping.items():
        result[canonical] = body[original_col]

    result["nim"] = result["nim"].apply(normalize_nim)
    result = result[result["nim"].ne("")].copy()
    result["nama_nilai"] = result["nama_nilai"].apply(normalize_text) if "nama_nilai" in result.columns else ""
    return result.reset_index(drop=True)


def read_penilaian_tashih_file(uploaded_file) -> pd.DataFrame:
    """Baca file penilaian tashih yang headernya tidak berada di baris pertama."""
    filename = uploaded_file.name.lower()
    if not filename.endswith((".xlsx", ".xls")):
        raise ValueError("Format file tidak didukung. Gunakan .xlsx atau .xls")

    uploaded_file.seek(0)
    sheets = pd.read_excel(uploaded_file, sheet_name=None, header=None, dtype=str)

    frames: List[pd.DataFrame] = []
    for sheet_df in sheets.values():
        extracted = _extract_penilaian_sheet(sheet_df)
        if extracted is not None and not extracted.empty:
            frames.append(extracted)

    if not frames:
        return pd.DataFrame(columns=["nama_nilai", "nim", "total_nilai"])
    return pd.concat(frames, ignore_index=True, sort=False)


def compute_jilid(total: float) -> str:
    if total <= 25:
        return "Jilid 1"
    if total <= 50:
        return "Jilid 2"
    if total <= 75:
        return "Jilid 3"
    return "Jilid 4"


def build_jilid_recap(master_df: pd.DataFrame, penilaian_df: pd.DataFrame) -> Dict[str, Any]:
    """Gabungkan file penilaian dengan data master lalu kelompokkan per Jilid & jenis kelamin."""
    penilaian = penilaian_df.copy()
    penilaian["total_score"] = penilaian["total_nilai"].apply(parse_score)

    duplicate_nim_rows = penilaian[penilaian["nim"].ne("") & penilaian["nim"].duplicated(keep=False)]
    penilaian_unique = penilaian.drop_duplicates(subset=["nim"], keep="last")

    merged = penilaian_unique.merge(master_df, on="nim", how="left", suffixes=("_nilai", ""))

    problems: List[Dict[str, Any]] = []

    for _, row in duplicate_nim_rows.iterrows():
        problems.append({
            "NIM": row.get("nim", ""),
            "Nama": row.get("nama_nilai", ""),
            "Program Studi": row.get("prodi_nilai", ""),
            "Total Nilai": row.get("total_nilai", ""),
            "Keterangan": "NIM duplikat di file penilaian tashih. Sistem memakai data terakhir saat menghitung jilid.",
        })

    valid_mask: List[bool] = []
    jilid_values: List[str] = []

    for _, row in merged.iterrows():
        reasons: List[str] = []
        master_found = not is_blank(row.get("kode_kelas_pai", ""))
        if not master_found:
            reasons.append("NIM tidak ditemukan di file master")
        elif row.get("jenis_kelamin") not in ("L", "P"):
            reasons.append("Jenis kelamin tidak dikenali di file master")

        total_score = row.get("total_score")
        if total_score is None:
            reasons.append("Total Nilai kosong atau tidak valid")
        elif not (JILID_TOTAL_RANGE["min"] <= total_score <= JILID_TOTAL_RANGE["max"]):
            reasons.append(
                f"Total Nilai di luar rentang {JILID_TOTAL_RANGE['min']:g}-{JILID_TOTAL_RANGE['max']:g} ({total_score:g})"
            )

        if reasons:
            valid_mask.append(False)
            jilid_values.append("")
            prodi_display = row.get("prodi") if master_found and not is_blank(row.get("prodi", "")) else row.get("prodi_nilai", "")
            problems.append({
                "NIM": row.get("nim", ""),
                "Nama": row.get("nama") if master_found and not is_blank(row.get("nama", "")) else row.get("nama_nilai", ""),
                "Program Studi": prodi_display,
                "Total Nilai": row.get("total_nilai", ""),
                "Keterangan": "; ".join(reasons),
            })
        else:
            valid_mask.append(True)
            jilid_values.append(compute_jilid(total_score))

    merged["_valid"] = valid_mask
    merged["_jilid"] = jilid_values

    valid_rows = merged[merged["_valid"]].copy()

    groups: Dict[Tuple[str, str], pd.DataFrame] = {}
    ringkasan_rows: List[Dict[str, Any]] = []
    for jilid_label in JILID_LABELS:
        for gender_code, gender_label in JILID_GENDER_SHEET_LABELS:
            subset = valid_rows[
                (valid_rows["_jilid"] == jilid_label) & (valid_rows["jenis_kelamin"] == gender_code)
            ].copy()
            sort_keys = subset["kode_kelas_pai"].apply(natural_sort_kelas_key)
            subset["_sort_angka"] = sort_keys.apply(lambda x: x[0])
            subset["_sort_huruf"] = sort_keys.apply(lambda x: x[1])
            subset["_sort_asli"] = sort_keys.apply(lambda x: x[2])
            subset = subset.sort_values(
                by=["_sort_angka", "_sort_huruf", "_sort_asli", "nama"], ascending=True
            ).drop(columns=["_sort_angka", "_sort_huruf", "_sort_asli"])
            groups[(jilid_label, gender_code)] = subset[JILID_OUTPUT_COLUMNS].reset_index(drop=True)
            ringkasan_rows.append({
                "Jilid": jilid_label,
                "Jenis Kelamin": gender_label,
                "Jumlah": int(len(subset)),
            })

    ringkasan = pd.DataFrame(ringkasan_rows)
    data_bermasalah = pd.DataFrame(problems, columns=["NIM", "Nama", "Program Studi", "Total Nilai", "Keterangan"])

    summary = {
        "total_dinilai": int(len(penilaian)),
        "total_terklasifikasi": int(len(valid_rows)),
        "total_bermasalah": int(len(data_bermasalah)),
    }

    return {
        "groups": groups,
        "ringkasan": ringkasan,
        "data_bermasalah": data_bermasalah,
        "summary": summary,
    }


def export_jilid_excel(groups: Dict[Tuple[str, str], pd.DataFrame], data_bermasalah: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for jilid_label in JILID_LABELS:
            for gender_code, gender_label in JILID_GENDER_SHEET_LABELS:
                group = groups.get((jilid_label, gender_code))
                if group is None:
                    group = pd.DataFrame(columns=JILID_OUTPUT_COLUMNS)
                sheet_name = jilid_sheet_name(jilid_label, gender_label)
                labeled = group.rename(columns=JILID_OUTPUT_COLUMN_LABELS)
                labeled.to_excel(writer, sheet_name=sheet_name, index=False)
        data_bermasalah.to_excel(writer, sheet_name="Data Bermasalah", index=False)
    return output.getvalue()
