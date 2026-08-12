import re
import zipfile
from difflib import SequenceMatcher
from io import BytesIO
from typing import Dict, List, Tuple, Any

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# KONFIGURASI UTAMA
# ============================================================

APP_TITLE = "Rekap Nilai TQQ Akbar UNESA"
MODE_REKAP = "Mode Rekap Peserta & Nilai"
MODE_RAPIKAN = "Mode Rapikan Hasil Rekap"

PESERTA_REQUIRED_COLUMNS = [
    "Nama",
    "NIM",
    "Prodi",
    "Kelas Umum",
    "Kode Kelas PAI",
    "Dosen Pengampu",
]

NILAI_REQUIRED_COLUMNS = [
    "NAMA",
    "NIM",
    "PRESENSI",
    "BACAAN",
    "HAFALAN",
    "EVALUASI",
    "TOTAL NILAI",
    "ABJAD",
]

PESERTA_COLUMN_ALIASES = {
    "nama": ["Nama", "NAMA", "nama"],
    "nim": ["NIM", "Nim", "nim", "NPM", "npm", "No Induk", "Nomor Induk"],
    "prodi": ["Prodi", "PRODI", "prodi", "Program Studi", "PROGRAM STUDI", "program studi"],
    "kelas_umum": ["Kelas Umum", "KELAS UMUM", "kelas umum", "Kelas Asal", "KELAS ASAL", "kelas asal"],
    "kode_kelas_pai": [
        "Kode Kelas PAI", "KODE KELAS PAI", "kode kelas pai", "Kelas PAI", "KELAS PAI",
        "kelas pai", "Kode PAI", "KODE PAI", "kode pai",
    ],
    "dosen_pengampu": [
        "Dosen Pengampu", "DOSEN PENGAMPU", "dosen pengampu", "Dosen", "DOSEN", "dosen",
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

REKAP_REQUIRED_COLUMN_LABELS = {
    "nim": "NIM",
    "prodi": "Prodi",
    "kode_kelas_pai": "Kode Kelas PAI",
}

REKAP_INTERNAL_COLUMNS = {
    "nim": "__rekap_nim",
    "prodi": "__rekap_prodi",
    "kode_kelas_pai": "__rekap_kode_kelas_pai",
}

FINAL_COLUMNS = [
    "nama", "nim", "prodi", "kelas_umum", "kode_kelas_pai", "dosen_pengampu",
    "nama_nilai", "presensi", "bacaan", "hafalan", "evaluasi", "total_nilai", "abjad",
    "status_nilai", "status_validasi", "catatan_validasi",
]

FINAL_COLUMN_LABELS = {
    "nama": "Nama",
    "nim": "NIM",
    "prodi": "Prodi",
    "kelas_umum": "Kelas Umum",
    "kode_kelas_pai": "Kode Kelas PAI",
    "dosen_pengampu": "Dosen Pengampu",
    "nama_nilai": "Nama dari File Nilai",
    "presensi": "Presensi",
    "bacaan": "Bacaan",
    "hafalan": "Hafalan",
    "evaluasi": "Evaluasi",
    "total_nilai": "Total Nilai",
    "abjad": "Abjad",
    "status_nilai": "Status Nilai",
    "status_validasi": "Status Validasi",
    "catatan_validasi": "Catatan Validasi",
}

# Kolom khusus untuk export final per Kode Kelas PAI.
# Export utama sengaja tidak menyertakan kolom status/catatan validasi agar file final siap dibagikan.
EXPORT_PER_KELAS_COLUMNS = [
    "nama",
    "nim",
    "prodi",
    "kelas_umum",
    "kode_kelas_pai",
    "dosen_pengampu",
    "presensi",
    "bacaan",
    "hafalan",
    "evaluasi",
    "total_nilai",
    "abjad",
]

EXPORT_PER_KELAS_COLUMN_LABELS = {
    "nama": "Nama",
    "nim": "NIM",
    "prodi": "Prodi",
    "kelas_umum": "Kelas Umum",
    "kode_kelas_pai": "Kode Kelas PAI",
    "dosen_pengampu": "Dosen Pengampu",
    "presensi": "PRESENSI",
    "bacaan": "BACAAN",
    "hafalan": "HAFALAN",
    "evaluasi": "EVALUASI",
    "total_nilai": "TOTAL NILAI",
    "abjad": "ABJAD",
}

# Jenis masalah yang ditampilkan di menu Validasi dan grafik.
# Urutan ini mengikuti kebutuhan final panitia.
PROBLEM_TYPE_ORDER = [
    "NIM di file nilai tidak ada di file peserta",
    "Abjad kosong",
    "Total Nilai kosong",
    "Nama berbeda antara file peserta dan file nilai",
    "NIM duplikat di file nilai",
    "Nilai tidak valid atau di luar rentang",
]

# Rentang nilai default.
# Batas ini sengaja dibuat umum 0-100 agar aman untuk tahap awal.
# Jika format penilaian berubah, cukup ubah angka min/max di sini.
SCORE_RANGE_CONFIG = {
    "presensi": {"label": "PRESENSI", "min": 0, "max": 100},
    "bacaan": {"label": "BACAAN", "min": 0, "max": 100},
    "hafalan": {"label": "HAFALAN", "min": 0, "max": 100},
    "evaluasi": {"label": "EVALUASI", "min": 0, "max": 100},
    "total_nilai": {"label": "TOTAL NILAI", "min": 0, "max": 100},
}

# ============================================================
# HELPER UMUM
# ============================================================

def normalize_header(value: Any) -> str:
    text = str(value).strip().lower()
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def normalize_nim(value: Any) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if re.fullmatch(r"\d+\.0", text):
        text = text[:-2]
    text = re.sub(r"\s+", "", text)
    return text


def normalize_name_for_compare(value: Any) -> str:
    text = normalize_text(value).lower()
    text = text.replace(".", " ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def name_similarity(name_a: Any, name_b: Any) -> float:
    a = normalize_name_for_compare(name_a)
    b = normalize_name_for_compare(name_b)
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


def safe_sheet_name(name: str) -> str:
    cleaned = re.sub(r"[\[\]\:\*\?\/\\]", "-", str(name))
    cleaned = cleaned.strip() or "Tanpa Kelas"
    return cleaned[:31]


def safe_filename_part(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_\-]+", "_", normalize_text(name))
    return cleaned.strip("_") or "tanpa_kelas"


def natural_sort_kelas_key(value: Any) -> Tuple[int, str, str]:
    text = normalize_text(value).upper()
    match = re.match(r"^(\d+)\s*([A-Z]+)?", text)
    if match:
        number = int(match.group(1))
        letter = match.group(2) or ""
        return number, letter, text
    return 9999, text, text


def is_blank(value: Any) -> bool:
    return pd.isna(value) or str(value).strip() == "" or str(value).strip().lower() in {"nan", "none", "-"}


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


def detect_column_mapping(df: pd.DataFrame, aliases: Dict[str, List[str]]) -> Tuple[Dict[str, str], List[str]]:
    normalized_columns = {normalize_header(col): col for col in df.columns}
    mapping: Dict[str, str] = {}
    missing: List[str] = []

    for canonical, possible_names in aliases.items():
        found = None
        for alias in possible_names:
            normalized_alias = normalize_header(alias)
            if normalized_alias in normalized_columns:
                found = normalized_columns[normalized_alias]
                break
        if found:
            mapping[canonical] = found
        else:
            missing.append(canonical)

    return mapping, missing


def canonical_to_required_label(canonical_name: str, file_type: str) -> str:
    if file_type == "peserta":
        return FINAL_COLUMN_LABELS.get(canonical_name, canonical_name)
    label_map = {
        "nama_nilai": "NAMA",
        "nim": "NIM",
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

    for col in standardized.columns:
        if col != "nim":
            standardized[col] = standardized[col].apply(lambda x: "" if pd.isna(x) else str(x).strip())

    return standardized, []


class RekapRequiredColumnError(ValueError):
    """Error khusus ketika file hasil rekap tidak memiliki kolom wajib."""


def read_uploaded_file(uploaded_file) -> pd.DataFrame:
    filename = uploaded_file.name.lower()
    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file, dtype=str)
    if filename.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file, dtype=str)
    raise ValueError("Format file tidak didukung. Gunakan .xlsx, .xls, atau .csv")


def drop_empty_rekap_rows(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    non_empty_mask = ~df.apply(lambda row: all(is_blank(value) for value in row), axis=1)
    return df.loc[non_empty_mask].copy()


def normalize_rekap_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """Menstandarkan kolom wajib dan menambahkan kolom internal untuk grouping."""
    mapping, missing = detect_column_mapping(df, REKAP_COLUMN_ALIASES)
    if missing:
        missing_labels = [REKAP_REQUIRED_COLUMN_LABELS[col] for col in missing]
        return df.copy(), missing_labels

    normalized = df.copy()
    required_columns: Dict[str, str] = {}
    rename_map: Dict[str, str] = {}

    for canonical, original_col in mapping.items():
        target_col = REKAP_REQUIRED_COLUMN_LABELS[canonical]
        if original_col != target_col and target_col not in normalized.columns:
            rename_map[original_col] = target_col
            required_columns[canonical] = target_col
        else:
            required_columns[canonical] = original_col

    if rename_map:
        normalized = normalized.rename(columns=rename_map)

    normalized[REKAP_INTERNAL_COLUMNS["nim"]] = normalized[required_columns["nim"]].apply(normalize_nim)
    normalized[REKAP_INTERNAL_COLUMNS["prodi"]] = normalized[required_columns["prodi"]].apply(normalize_text)
    normalized[REKAP_INTERNAL_COLUMNS["kode_kelas_pai"]] = normalized[required_columns["kode_kelas_pai"]].apply(normalize_text)
    return normalized, []


def read_rekap_file(uploaded_file) -> pd.DataFrame:
    """Membaca semua sheet file hasil rekap dan menggabungkan sheet yang berisi data."""
    filename = uploaded_file.name.lower()
    if not filename.endswith((".xlsx", ".xls")):
        raise ValueError("Format file tidak didukung. Gunakan .xlsx atau .xls")

    uploaded_file.seek(0)
    sheets = pd.read_excel(uploaded_file, sheet_name=None, dtype=str)
    frames: List[pd.DataFrame] = []

    for sheet_name, sheet_df in sheets.items():
        cleaned_df = drop_empty_rekap_rows(sheet_df)
        if cleaned_df.empty:
            continue

        normalized_df, missing = normalize_rekap_columns(cleaned_df)
        if missing:
            missing_text = ", ".join(missing)
            raise RekapRequiredColumnError(f"Sheet '{sheet_name}' belum memiliki kolom: {missing_text}")

        frames.append(normalized_df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True, sort=False)


def drop_rekap_internal_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=list(REKAP_INTERNAL_COLUMNS.values()), errors="ignore")


def clean_sheet_name(name: str, existing_names: set[str]) -> str:
    """Membersihkan nama sheet Excel, memotong ke 31 karakter, dan menjaga tetap unik."""
    cleaned = re.sub(r"[\:\?\/\\\*\[\]]", " ", str(name))
    cleaned = re.sub(r"\s+", " ", cleaned).strip() or "Sheet"
    base_name = cleaned[:31].strip() or "Sheet"
    sheet_name = base_name

    used_lower = {existing_name.lower() for existing_name in existing_names}
    counter = 2
    while sheet_name.lower() in used_lower:
        suffix = f" {counter}"
        max_base_length = 31 - len(suffix)
        trimmed_base = base_name[:max_base_length].strip() or "Sheet"[:max_base_length]
        sheet_name = f"{trimmed_base}{suffix}"[:31]
        counter += 1

    existing_names.add(sheet_name)
    return sheet_name


def sort_rekap_group_by_nim(group: pd.DataFrame) -> pd.DataFrame:
    sorted_group = group.copy()
    nim_col = REKAP_INTERNAL_COLUMNS["nim"]
    sorted_group["_rekap_sort_nim_text"] = sorted_group[nim_col].apply(normalize_nim)
    sorted_group["_rekap_sort_nim_number"] = pd.to_numeric(sorted_group["_rekap_sort_nim_text"], errors="coerce")
    sorted_group["_rekap_sort_nim_is_text"] = sorted_group["_rekap_sort_nim_number"].isna()
    sorted_group = sorted_group.sort_values(
        by=["_rekap_sort_nim_is_text", "_rekap_sort_nim_number", "_rekap_sort_nim_text"],
        ascending=True,
        na_position="last",
        kind="mergesort",
    )
    return sorted_group.drop(
        columns=["_rekap_sort_nim_text", "_rekap_sort_nim_number", "_rekap_sort_nim_is_text"],
        errors="ignore",
    )


def split_rekap_by_kelas_prodi(df: pd.DataFrame) -> List[Tuple[str, str, pd.DataFrame]]:
    kelas_col = REKAP_INTERNAL_COLUMNS["kode_kelas_pai"]
    prodi_col = REKAP_INTERNAL_COLUMNS["prodi"]
    if df.empty or kelas_col not in df.columns or prodi_col not in df.columns:
        return []

    groups: List[Tuple[str, str, pd.DataFrame]] = []
    for (kelas, prodi), group in df.groupby([kelas_col, prodi_col], dropna=False, sort=False):
        kelas_label = "Tanpa Kelas" if is_blank(kelas) else normalize_text(kelas)
        prodi_label = "Tanpa Prodi" if is_blank(prodi) else normalize_text(prodi)
        groups.append((kelas_label, prodi_label, sort_rekap_group_by_nim(group)))

    groups.sort(key=lambda item: (natural_sort_kelas_key(item[0]), item[1].lower()))
    return groups


def build_rekap_kelas_prodi_preview(df: pd.DataFrame) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    existing_names: set[str] = set()
    for kelas_label, prodi_label, group in split_rekap_by_kelas_prodi(df):
        rows.append({
            "Kode Kelas PAI": kelas_label,
            "Prodi": prodi_label,
            "Nama Sheet": clean_sheet_name(f"{kelas_label} - {prodi_label}", existing_names),
            "Jumlah Data": int(len(group)),
        })
    return pd.DataFrame(rows)


def export_rekap_by_kelas_prodi(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    groups = split_rekap_by_kelas_prodi(df)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        if not groups:
            drop_rekap_internal_columns(df).to_excel(writer, sheet_name="Data Kosong", index=False)
        else:
            existing_names: set[str] = set()
            for kelas_label, prodi_label, group in groups:
                sheet_name = clean_sheet_name(f"{kelas_label} - {prodi_label}", existing_names)
                drop_rekap_internal_columns(group).to_excel(writer, sheet_name=sheet_name, index=False)

    return output.getvalue()


def create_template_excel() -> bytes:
    peserta_df = pd.DataFrame(columns=PESERTA_REQUIRED_COLUMNS)
    nilai_df = pd.DataFrame(columns=NILAI_REQUIRED_COLUMNS)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        peserta_df.to_excel(writer, sheet_name="Template Peserta", index=False)
        nilai_df.to_excel(writer, sheet_name="Template Nilai", index=False)
    return output.getvalue()


def reorder_and_rename(df: pd.DataFrame) -> pd.DataFrame:
    available_cols = [col for col in FINAL_COLUMNS if col in df.columns]
    result = df[available_cols].copy()
    return result.rename(columns=FINAL_COLUMN_LABELS)


def reorder_export_per_kelas(df: pd.DataFrame) -> pd.DataFrame:
    """Menyusun kolom final khusus export per Kode Kelas PAI."""
    result = pd.DataFrame()
    for col in EXPORT_PER_KELAS_COLUMNS:
        label = EXPORT_PER_KELAS_COLUMN_LABELS[col]
        if col in df.columns:
            result[label] = df[col]
        else:
            result[label] = ""
    return result


def add_problem(
    problems: List[Dict[str, Any]],
    sumber: str,
    jenis: str,
    nim: Any = "",
    nama_peserta: Any = "",
    nama_nilai: Any = "",
    kode_kelas_pai: Any = "",
    dosen_pengampu: Any = "",
    keterangan: str = "",
    kolom: str = "",
    nilai_terdeteksi: Any = "",
):
    problems.append({
        "Sumber": sumber,
        "Jenis Masalah": jenis,
        "NIM": normalize_text(nim),
        "Nama File Peserta": normalize_text(nama_peserta),
        "Nama File Nilai": normalize_text(nama_nilai),
        "Kode Kelas PAI": normalize_text(kode_kelas_pai),
        "Dosen Pengampu": normalize_text(dosen_pengampu),
        "Kolom": normalize_text(kolom),
        "Nilai Terdeteksi": normalize_text(nilai_terdeteksi),
        "Keterangan": keterangan,
    })


def build_problem_table(
    peserta_df: pd.DataFrame,
    nilai_df: pd.DataFrame,
    rekap: pd.DataFrame,
    unmatched_nilai: pd.DataFrame,
) -> pd.DataFrame:
    """Membuat daftar masalah utama sesuai kebutuhan panitia.

    Jenis masalah utama yang dicek:
    1. NIM di file nilai tidak ada di file peserta
    2. Abjad kosong
    3. Total Nilai kosong
    4. Nama berbeda antara file peserta dan file nilai
    5. NIM duplikat di file nilai
    6. Nilai tidak valid atau di luar rentang
    """
    problems: List[Dict[str, Any]] = []

    # 1. NIM di file nilai tidak ada di file peserta
    for _, row in unmatched_nilai.iterrows():
        add_problem(
            problems,
            "File Nilai",
            "NIM di file nilai tidak ada di file peserta",
            row.get("nim", ""),
            "",
            row.get("nama_nilai", ""),
            "",
            "",
            "Ada nilai untuk NIM ini, tetapi NIM tidak ditemukan di file peserta."
        )

    # 2. Abjad kosong
    for _, row in rekap[rekap["abjad"].apply(is_blank)].iterrows():
        add_problem(
            problems,
            "File Nilai",
            "Abjad kosong",
            row.get("nim", ""),
            row.get("nama", ""),
            row.get("nama_nilai", ""),
            row.get("kode_kelas_pai", ""),
            row.get("dosen_pengampu", ""),
            "Kolom ABJAD kosong atau peserta belum ditemukan di file nilai."
        )

    # 3. Total Nilai kosong
    for _, row in rekap[rekap["total_nilai"].apply(is_blank)].iterrows():
        add_problem(
            problems,
            "File Nilai",
            "Total Nilai kosong",
            row.get("nim", ""),
            row.get("nama", ""),
            row.get("nama_nilai", ""),
            row.get("kode_kelas_pai", ""),
            row.get("dosen_pengampu", ""),
            "Kolom TOTAL NILAI kosong atau peserta belum ditemukan di file nilai."
        )

    # 4. Nama berbeda antara file peserta dan file nilai
    for _, row in rekap[rekap["nama_berbeda"].fillna(False)].iterrows():
        add_problem(
            problems,
            "Gabungan Peserta + Nilai",
            "Nama berbeda antara file peserta dan file nilai",
            row.get("nim", ""),
            row.get("nama", ""),
            row.get("nama_nilai", ""),
            row.get("kode_kelas_pai", ""),
            row.get("dosen_pengampu", ""),
            f"Kemiripan nama sekitar {row.get('kemiripan_nama', 0):.0%}. Perlu dicek manual."
        )

    # 5. NIM duplikat di file nilai
    duplicate_nilai = nilai_df[nilai_df["nim"].ne("") & nilai_df["nim"].duplicated(keep=False)]
    for _, row in duplicate_nilai.iterrows():
        add_problem(
            problems,
            "File Nilai",
            "NIM duplikat di file nilai",
            row.get("nim", ""),
            "",
            row.get("nama_nilai", ""),
            "",
            "",
            "NIM muncul lebih dari sekali di file nilai. Sistem memakai data terakhir saat rekap."
        )

    # 6. Cek rentang nilai
    for _, row in rekap.iterrows():
        for col, config in SCORE_RANGE_CONFIG.items():
            issue = score_range_issue(row.get(col, ""), config["min"], config["max"])
            if issue:
                add_problem(
                    problems,
                    "File Nilai",
                    "Nilai tidak valid atau di luar rentang",
                    row.get("nim", ""),
                    row.get("nama", ""),
                    row.get("nama_nilai", ""),
                    row.get("kode_kelas_pai", ""),
                    row.get("dosen_pengampu", ""),
                    f"Kolom {config['label']} bernilai '{normalize_text(row.get(col, ''))}' dan {issue}. Rentang yang diterima: {config['min']:g}-{config['max']:g}.",
                    kolom=config["label"],
                    nilai_terdeteksi=row.get(col, ""),
                )

    columns = [
        "Sumber", "Jenis Masalah", "NIM", "Nama File Peserta", "Nama File Nilai",
        "Kode Kelas PAI", "Dosen Pengampu", "Kolom", "Nilai Terdeteksi", "Keterangan",
    ]
    if not problems:
        return pd.DataFrame(columns=columns)

    result = pd.DataFrame(problems, columns=columns)
    result["_urutan_masalah"] = result["Jenis Masalah"].apply(
        lambda value: PROBLEM_TYPE_ORDER.index(value) if value in PROBLEM_TYPE_ORDER else 999
    )
    result = result.sort_values(
        by=["_urutan_masalah", "Kode Kelas PAI", "NIM", "Nama File Peserta", "Nama File Nilai"],
        ascending=True,
        na_position="last",
    ).drop(columns=["_urutan_masalah"])
    return result


def process_rekap(peserta_df: pd.DataFrame, nilai_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    peserta_clean = peserta_df.dropna(how="all").copy()
    nilai_clean = nilai_df.dropna(how="all").copy()

    peserta_clean["nim"] = peserta_clean["nim"].apply(normalize_nim)
    nilai_clean["nim"] = nilai_clean["nim"].apply(normalize_nim)

    peserta_for_merge = peserta_clean[peserta_clean["nim"].ne("")].copy()
    nilai_for_merge = nilai_clean[nilai_clean["nim"].ne("")].copy()

    peserta_unique = peserta_for_merge.drop_duplicates(subset=["nim"], keep="first").copy()
    nilai_unique = nilai_for_merge.drop_duplicates(subset=["nim"], keep="last").copy()

    unmatched_nilai = nilai_unique[~nilai_unique["nim"].isin(peserta_unique["nim"])].copy()

    rekap = peserta_unique.merge(nilai_unique, on="nim", how="left", suffixes=("", "_nilai_file"))

    rekap["status_nilai"] = rekap.apply(
        lambda row: "Belum Ada Nilai" if is_blank(row.get("total_nilai", "")) and is_blank(row.get("abjad", "")) else "Sudah Ada Nilai",
        axis=1,
    )

    rekap["kemiripan_nama"] = rekap.apply(
        lambda row: name_similarity(row.get("nama", ""), row.get("nama_nilai", ""))
        if not is_blank(row.get("nama_nilai", "")) else 1.0,
        axis=1,
    )
    rekap["nama_berbeda"] = rekap.apply(
        lambda row: (not is_blank(row.get("nama_nilai", ""))) and row.get("kemiripan_nama", 1.0) < 0.88,
        axis=1,
    )

    def validation_notes(row: pd.Series) -> str:
        notes: List[str] = []
        if bool(row.get("nama_berbeda", False)):
            notes.append("Nama berbeda")
        if is_blank(row.get("abjad", "")):
            notes.append("Abjad kosong")
        if is_blank(row.get("total_nilai", "")):
            notes.append("Total Nilai kosong")
        notes.extend(get_score_range_notes(row))
        return "; ".join(notes) if notes else "-"

    rekap["catatan_validasi"] = rekap.apply(validation_notes, axis=1)
    rekap["status_validasi"] = rekap["catatan_validasi"].apply(lambda x: "Valid" if x == "-" else "Perlu Dicek")

    sort_keys = rekap["kode_kelas_pai"].apply(natural_sort_kelas_key)
    rekap["_sort_angka"] = sort_keys.apply(lambda x: x[0])
    rekap["_sort_huruf"] = sort_keys.apply(lambda x: x[1])
    rekap["_sort_asli"] = sort_keys.apply(lambda x: x[2])
    rekap = rekap.sort_values(
        by=["_sort_angka", "_sort_huruf", "_sort_asli", "nama"],
        ascending=True,
        na_position="last",
    ).drop(columns=["_sort_angka", "_sort_huruf", "_sort_asli"])

    sudah_ada_nilai = rekap[rekap["status_nilai"] == "Sudah Ada Nilai"].copy()
    belum_ada_nilai = rekap[rekap["status_nilai"] == "Belum Ada Nilai"].copy()
    perlu_dicek = rekap[rekap["status_validasi"] == "Perlu Dicek"].copy()

    ringkasan = (
        rekap.groupby("kode_kelas_pai", dropna=False)
        .agg(
            total_peserta=("nim", "count"),
            sudah_ada_nilai=("status_nilai", lambda x: (x == "Sudah Ada Nilai").sum()),
            belum_ada_nilai=("status_nilai", lambda x: (x == "Belum Ada Nilai").sum()),
            perlu_dicek=("status_validasi", lambda x: (x == "Perlu Dicek").sum()),
        )
        .reset_index()
    )

    if not ringkasan.empty:
        ringkasan["persentase_selesai"] = ringkasan.apply(
            lambda row: (row["sudah_ada_nilai"] / row["total_peserta"] * 100) if row["total_peserta"] else 0,
            axis=1,
        )
        sort_keys_ringkasan = ringkasan["kode_kelas_pai"].apply(natural_sort_kelas_key)
        ringkasan["_sort_angka"] = sort_keys_ringkasan.apply(lambda x: x[0])
        ringkasan["_sort_huruf"] = sort_keys_ringkasan.apply(lambda x: x[1])
        ringkasan["_sort_asli"] = sort_keys_ringkasan.apply(lambda x: x[2])
        ringkasan = ringkasan.sort_values(by=["_sort_angka", "_sort_huruf", "_sort_asli"]).drop(
            columns=["_sort_angka", "_sort_huruf", "_sort_asli"]
        )

    ringkasan = ringkasan.rename(columns={
        "kode_kelas_pai": "Kode Kelas PAI",
        "total_peserta": "Total Peserta",
        "sudah_ada_nilai": "Sudah Ada Nilai",
        "belum_ada_nilai": "Belum Ada Nilai",
        "perlu_dicek": "Perlu Dicek",
        "persentase_selesai": "Persentase Selesai (%)",
    })

    data_bermasalah = build_problem_table(peserta_clean, nilai_clean, rekap, unmatched_nilai)
    masalah_ringkasan = (
        data_bermasalah["Jenis Masalah"].value_counts().reset_index()
        if not data_bermasalah.empty else pd.DataFrame(columns=["Jenis Masalah", "Jumlah"])
    )
    if not masalah_ringkasan.empty:
        masalah_ringkasan.columns = ["Jenis Masalah", "Jumlah"]
        masalah_ringkasan["_urutan_masalah"] = masalah_ringkasan["Jenis Masalah"].apply(
            lambda value: PROBLEM_TYPE_ORDER.index(value) if value in PROBLEM_TYPE_ORDER else 999
        )
        masalah_ringkasan = masalah_ringkasan.sort_values(
            by=["_urutan_masalah", "Jenis Masalah"],
            ascending=True,
        ).drop(columns=["_urutan_masalah"])

    return {
        "rekap": rekap,
        "sudah_ada_nilai": sudah_ada_nilai,
        "belum_ada_nilai": belum_ada_nilai,
        "perlu_dicek": perlu_dicek,
        "ringkasan": ringkasan,
        "data_bermasalah": data_bermasalah,
        "masalah_ringkasan": masalah_ringkasan,
        "unmatched_nilai": unmatched_nilai,
    }


def export_excel(results: Dict[str, pd.DataFrame], include_per_kelas: bool = True) -> bytes:
    """
    Export utama: 1 file Excel berisi banyak sheet per Kode Kelas PAI.

    Setiap sheet hanya berisi kolom final:
    Nama, NIM, Prodi, Kelas Umum, Kode Kelas PAI, Dosen Pengampu,
    PRESENSI, BACAAN, HAFALAN, EVALUASI, TOTAL NILAI, ABJAD.
    """
    output = BytesIO()
    rekap = results["rekap"].copy()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        if rekap.empty:
            pd.DataFrame(columns=list(EXPORT_PER_KELAS_COLUMN_LABELS.values())).to_excel(
                writer,
                sheet_name="Data Kosong",
                index=False,
            )
        else:
            used_sheet_names = set()
            for kelas, group in rekap.groupby("kode_kelas_pai", dropna=False, sort=False):
                kelas_label = "Tanpa Kelas" if is_blank(kelas) else str(kelas).strip()
                base_sheet_name = safe_sheet_name(kelas_label)
                sheet_name = base_sheet_name

                # Hindari error jika ada nama sheet yang sama setelah dipotong/dirapikan.
                counter = 2
                while sheet_name in used_sheet_names:
                    suffix = f"_{counter}"
                    sheet_name = safe_sheet_name(base_sheet_name[: 31 - len(suffix)] + suffix)
                    counter += 1

                used_sheet_names.add(sheet_name)
                reorder_export_per_kelas(group).to_excel(writer, sheet_name=sheet_name, index=False)

    return output.getvalue()


def export_data_bermasalah_excel(results: Dict[str, pd.DataFrame]) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        results["masalah_ringkasan"].to_excel(writer, sheet_name="Ringkasan Masalah", index=False)
        results["data_bermasalah"].to_excel(writer, sheet_name="Data Bermasalah", index=False)
        reorder_and_rename(results["perlu_dicek"]).to_excel(writer, sheet_name="Peserta Perlu Dicek", index=False)
    return output.getvalue()


def build_export_sheet_preview(results: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    rekap = results["rekap"].copy()
    if rekap.empty:
        return pd.DataFrame(columns=[
            "Kode Kelas PAI", "Nama Sheet", "Jumlah Peserta", "Sudah Ada Nilai",
            "Belum Ada Nilai", "Perlu Dicek", "Status Export",
        ])

    rows: List[Dict[str, Any]] = []
    used_sheet_names = set()
    for kelas, group in rekap.groupby("kode_kelas_pai", dropna=False, sort=False):
        kelas_label = "Tanpa Kelas" if is_blank(kelas) else str(kelas).strip()
        base_sheet_name = safe_sheet_name(kelas_label)
        sheet_name = base_sheet_name
        counter = 2
        while sheet_name in used_sheet_names:
            suffix = f"_{counter}"
            sheet_name = safe_sheet_name(base_sheet_name[: 31 - len(suffix)] + suffix)
            counter += 1
        used_sheet_names.add(sheet_name)

        perlu_dicek = int((group["status_validasi"] == "Perlu Dicek").sum())
        belum_ada = int((group["status_nilai"] == "Belum Ada Nilai").sum())
        rows.append({
            "Kode Kelas PAI": kelas_label,
            "Nama Sheet": sheet_name,
            "Jumlah Peserta": int(len(group)),
            "Sudah Ada Nilai": int((group["status_nilai"] == "Sudah Ada Nilai").sum()),
            "Belum Ada Nilai": belum_ada,
            "Perlu Dicek": perlu_dicek,
            "Status Export": "Perlu dicek" if perlu_dicek or belum_ada else "Aman",
        })

    return pd.DataFrame(rows)


def export_laporan_validasi_excel(results: Dict[str, pd.DataFrame]) -> bytes:
    output = BytesIO()
    data_bermasalah = results["data_bermasalah"].copy()
    preview_sheet = build_export_sheet_preview(results)

    rentang_df = pd.DataFrame([
        {
            "Kolom": config["label"],
            "Nilai Minimum": config["min"],
            "Nilai Maksimum": config["max"],
            "Keterangan": "Nilai kosong dicek sebagai masalah terpisah; validasi rentang hanya untuk nilai yang terisi.",
        }
        for config in SCORE_RANGE_CONFIG.values()
    ])

    laporan_ringkas = pd.DataFrame([
        {"Indikator": "Total Peserta", "Jumlah": len(results["rekap"])},
        {"Indikator": "Sudah Ada Nilai", "Jumlah": len(results["sudah_ada_nilai"])},
        {"Indikator": "Belum Ada Nilai", "Jumlah": len(results["belum_ada_nilai"])},
        {"Indikator": "Peserta Perlu Dicek", "Jumlah": len(results["perlu_dicek"])},
        {"Indikator": "Total Baris Masalah", "Jumlah": len(data_bermasalah)},
        {"Indikator": "Jumlah Sheet Export", "Jumlah": len(preview_sheet)},
    ])

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        laporan_ringkas.to_excel(writer, sheet_name="Ringkasan Validasi", index=False)
        results["masalah_ringkasan"].to_excel(writer, sheet_name="Ringkasan Masalah", index=False)
        preview_sheet.to_excel(writer, sheet_name="Preview Sheet Export", index=False)
        rentang_df.to_excel(writer, sheet_name="Aturan Rentang Nilai", index=False)
        data_bermasalah.to_excel(writer, sheet_name="Semua Masalah", index=False)
        reorder_and_rename(results["perlu_dicek"]).to_excel(writer, sheet_name="Peserta Perlu Dicek", index=False)

        if not data_bermasalah.empty:
            used_sheet_names = {"Ringkasan Validasi", "Ringkasan Masalah", "Preview Sheet Export", "Aturan Rentang Nilai", "Semua Masalah", "Peserta Perlu Dicek"}
            for jenis, group in data_bermasalah.groupby("Jenis Masalah", sort=False):
                sheet_name = safe_sheet_name(str(jenis)[:31])
                base_sheet_name = sheet_name
                counter = 2
                while sheet_name in used_sheet_names:
                    suffix = f"_{counter}"
                    sheet_name = safe_sheet_name(base_sheet_name[: 31 - len(suffix)] + suffix)
                    counter += 1
                used_sheet_names.add(sheet_name)
                group.to_excel(writer, sheet_name=sheet_name, index=False)

    return output.getvalue()


def export_per_kelas_zip(results: Dict[str, pd.DataFrame]) -> bytes:
    zip_buffer = BytesIO()
    rekap = results["rekap"].copy()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for kelas, group in rekap.groupby("kode_kelas_pai", dropna=False):
            kelas_label = "Tanpa Kelas" if is_blank(kelas) else str(kelas)
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                reorder_and_rename(group).to_excel(writer, sheet_name=safe_sheet_name(kelas_label), index=False)
            filename = f"Rekap_Kelas_{safe_filename_part(kelas_label)}.xlsx"
            zip_file.writestr(filename, excel_buffer.getvalue())

    return zip_buffer.getvalue()


# ============================================================
# STREAMLIT UI - WEB DASHBOARD STYLE
# ============================================================

st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")


def inject_custom_css() -> None:
    st.markdown(
        """
        <style>
            :root {
                --primary: #1e40af;
                --primary-2: #2563eb;
                --accent: #0ea5e9;
                --navy: #0b2447;
                --navy-2: #123c69;
                --bg-soft: #f5f8ff;
                --card: #ffffff;
                --text-dark: #0f172a;
                --text-muted: #64748b;
                --border: #dbeafe;
                --blue-soft: #eff6ff;
            }

            .stApp {
                background: #f5f8ff;
            }

            [data-testid="stSidebar"] {
                background: #0b2447;
                border-right: 1px solid rgba(255,255,255,.08);
            }

            [data-testid="stSidebar"] .nav-title,
            [data-testid="stSidebar"] .nav-subtitle,
            [data-testid="stSidebar"] h1,
            [data-testid="stSidebar"] h2,
            [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] span {
                color: #f8fafc !important;
            }

            [data-testid="stSidebar"] input,
            [data-testid="stSidebar"] textarea {
                color: #0f172a !important;
                background: #ffffff !important;
            }

            [data-testid="stSidebar"] input::placeholder {
                color: #64748b !important;
                opacity: 1 !important;
            }

            [data-testid="stSidebar"] code {
                color: #0f172a !important;
                background: #dbeafe !important;
                border-radius: 8px;
                padding: 2px 6px;
            }

            [data-testid="stSidebar"] .stAlert {
                background: #1e3a8a !important;
                border: 1px solid rgba(191,219,254,.35) !important;
                border-radius: 16px !important;
            }

            [data-testid="stSidebar"] .stAlert * {
                color: #ffffff !important;
            }

            [data-testid="stSidebar"] .stButton button,
            [data-testid="stSidebar"] button {
                border-radius: 14px;
            }

            .block-container {
                padding-top: 1.4rem;
                padding-bottom: 3rem;
                max-width: 1450px;
            }

            .hero-card {
                padding: 30px 32px;
                border-radius: 28px;
                background: #1d4ed8;
                box-shadow: 0 22px 58px rgba(30, 64, 175, 0.18);
                margin-bottom: 22px;
                color: #ffffff;
                border: 1px solid #1e40af;
            }

            .hero-eyebrow {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 6px 12px;
                border-radius: 999px;
                background: #dbeafe;
                color: #1e3a8a;
                font-size: .88rem;
                font-weight: 850;
                margin-bottom: 12px;
            }

            .hero-title {
                color: #ffffff !important;
                font-size: 2.35rem;
                line-height: 1.05;
                font-weight: 950;
                margin: 0;
                letter-spacing: -0.045em;
            }

            .hero-subtitle {
                max-width: 920px;
                font-size: 1.02rem;
                color: #e0f2fe !important;
                margin-top: 12px;
                margin-bottom: 0;
            }

            .guide-card {
                padding: 18px 20px;
                border-radius: 22px;
                background: #ffffff;
                border: 1px solid var(--border);
                box-shadow: 0 12px 30px rgba(30, 64, 175, 0.07);
                margin-bottom: 18px;
            }

            .guide-title {
                color: var(--text-dark);
                font-size: 1.05rem;
                font-weight: 900;
                margin-bottom: 10px;
            }

            .guide-list {
                margin: 0;
                padding-left: 1.25rem;
                color: var(--text-dark);
                line-height: 1.75;
                font-weight: 650;
            }

            .guide-list li::marker {
                color: #1d4ed8;
                font-weight: 900;
            }

            .section-title {
                margin-top: 24px;
                margin-bottom: 8px;
                font-size: 1.46rem;
                font-weight: 900;
                color: var(--text-dark);
                letter-spacing: -0.025em;
            }

            .section-caption {
                margin-top: -2px;
                margin-bottom: 18px;
                color: var(--text-muted);
                font-size: .98rem;
            }

            .soft-card {
                background: #ffffff;
                border: 1px solid var(--border);
                border-radius: 24px;
                padding: 22px;
                box-shadow: 0 18px 45px rgba(30, 64, 175, 0.07);
                margin-bottom: 16px;
            }

            .metric-grid {
                display: grid;
                grid-template-columns: repeat(6, minmax(0, 1fr));
                gap: 14px;
                margin: 10px 0 22px 0;
            }

            .metric-card {
                background: #ffffff;
                border: 1px solid var(--border);
                border-radius: 22px;
                padding: 18px;
                min-height: 116px;
                box-shadow: 0 12px 35px rgba(30, 64, 175, 0.07);
                position: relative;
                overflow: hidden;
            }

            .metric-card:before {
                content: "";
                position: absolute;
                width: 92px;
                height: 92px;
                right: -32px;
                top: -34px;
                border-radius: 100px;
                background: #dbeafe;
            }

            .metric-label {
                color: var(--text-muted);
                font-weight: 800;
                font-size: .80rem;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: .04em;
            }

            .metric-value {
                color: var(--text-dark);
                font-size: 1.75rem;
                font-weight: 950;
                letter-spacing: -0.03em;
            }

            .metric-note {
                color: #2563eb;
                font-size: .82rem;
                margin-top: 4px;
                font-weight: 750;
            }

            .nav-brand {
                padding: 16px 10px 10px 10px;
            }

            .nav-title {
                font-size: 1.1rem;
                line-height: 1.2;
                font-weight: 950;
                color: #ffffff;
                margin-bottom: 6px;
            }

            .nav-subtitle {
                font-size: .82rem;
                color: #dbeafe;
                margin-bottom: 16px;
            }

            .sidebar-guide {
                background: #123c69;
                border: 1px solid rgba(191,219,254,.32);
                border-radius: 16px;
                padding: 14px 16px;
                margin: 12px 0 18px 0;
            }

            .sidebar-guide-title {
                color: #ffffff;
                font-weight: 900;
                margin-bottom: 8px;
            }

            .sidebar-guide ol {
                margin: 0;
                padding-left: 1.2rem;
            }

            .sidebar-guide li {
                color: #e0f2fe;
                font-size: .88rem;
                line-height: 1.55;
                margin-bottom: 5px;
            }

            .stButton > button,
            .stDownloadButton > button {
                border-radius: 16px !important;
                padding: .7rem 1rem !important;
                font-weight: 850 !important;
                border: 1px solid rgba(37,99,235,.20) !important;
                box-shadow: 0 10px 24px rgba(30, 64, 175, 0.10) !important;
            }

            .stFileUploader section {
                border-radius: 20px !important;
                border: 1.6px dashed #93c5fd !important;
                background: #ffffff !important;
            }

            [data-testid="stDataFrame"] {
                border-radius: 20px;
                overflow: hidden;
                box-shadow: 0 14px 35px rgba(30, 64, 175, 0.06);
            }

            div[data-testid="stExpander"] {
                border-radius: 20px !important;
                border-color: #dbeafe !important;
                background: #ffffff !important;
            }

            @media (max-width: 1200px) {
                .metric-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
            }
            @media (max-width: 760px) {
                .metric-grid { grid-template-columns: repeat(1, minmax(0, 1fr)); }
                .hero-title { font-size: 1.65rem; }
                .hero-card { padding: 22px; border-radius: 22px; }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

def format_number(value: int) -> str:
    return f"{int(value):,}".replace(",", ".")


def render_hero() -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-eyebrow">📊 Sistem Rekap Akademik TQQ Akbar</div>
            <h1 class="hero-title">{APP_TITLE}</h1>
            <p class="hero-subtitle">
                Upload dua file, validasi otomatis, cocokkan data berdasarkan NIM, lalu export hasil menjadi
                satu file Excel dengan banyak sheet per Kode Kelas PAI.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )




def render_process_steps(has_results: bool) -> None:
    if has_results:
        subtitle = "Data sudah diproses. Lanjutkan pengecekan pada dashboard, grafik, tabel rekap, validasi, lalu export."
    else:
        subtitle = "Ikuti panduan berikut dari atas ke bawah. Aplikasi tidak akan memproses otomatis sebelum tombol proses ditekan."
    st.markdown(
        f"""
        <div class="guide-card">
            <div class="guide-title">📌 Panduan Penggunaan</div>
            <ol class="guide-list">
                <li>Upload <b>File Peserta</b> dan <b>File Nilai</b> sesuai format kolom wajib.</li>
                <li>Klik tombol <b>Mulai Analisis / Rekap Data</b> untuk menjalankan pencocokan data.</li>
                <li>Cek <b>dashboard ringkasan</b> dan <b>grafik</b> untuk melihat progres nilai.</li>
                <li>Gunakan <b>filter hasil rekap</b> untuk mengecek data per Kode Kelas PAI, prodi, dosen, atau status.</li>
                <li>Periksa bagian <b>validasi data bermasalah</b> dan cek rentang nilai sebelum mengunduh hasil akhir.</li>
                <li>Lihat <b>preview sheet per Kode Kelas PAI</b>, lalu download Excel final atau laporan validasi.</li>
            </ol>
        </div>
        <div class="section-caption">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )

def render_metric_cards(results: Dict[str, pd.DataFrame]) -> None:
    rekap = results["rekap"]
    sudah_ada_nilai = results["sudah_ada_nilai"]
    belum_ada_nilai = results["belum_ada_nilai"]
    data_bermasalah = results["data_bermasalah"]
    jumlah_kelas = rekap["kode_kelas_pai"].replace("", pd.NA).dropna().nunique()
    persentase_selesai = (len(sudah_ada_nilai) / len(rekap) * 100) if len(rekap) else 0

    st.markdown(
        f"""
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-label">Total Peserta</div>
                <div class="metric-value">{format_number(len(rekap))}</div>
                <div class="metric-note">Data master peserta</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Sudah Ada Nilai</div>
                <div class="metric-value">{format_number(len(sudah_ada_nilai))}</div>
                <div class="metric-note">Siap direkap</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Belum Ada Nilai</div>
                <div class="metric-value">{format_number(len(belum_ada_nilai))}</div>
                <div class="metric-note">Perlu ditindaklanjuti</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Persentase Selesai</div>
                <div class="metric-value">{persentase_selesai:.1f}%</div>
                <div class="metric-note">Progress rekap</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Jumlah Kelas PAI</div>
                <div class="metric-value">{format_number(jumlah_kelas)}</div>
                <div class="metric-note">Kode kelas terdeteksi</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Data Bermasalah</div>
                <div class="metric-value">{format_number(len(data_bermasalah))}</div>
                <div class="metric-note">Butuh validasi</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(min(persentase_selesai / 100, 1.0), text=f"Progress nilai masuk: {persentase_selesai:.1f}%")


def make_options(series: pd.Series) -> List[str]:
    values = [str(v) for v in series.dropna().unique() if not is_blank(v)]
    values = sorted(values, key=lambda x: natural_sort_kelas_key(x) if re.match(r"^\d", x) else (9999, x, x))
    return ["Semua"] + values


def apply_filters(rekap: pd.DataFrame) -> pd.DataFrame:
    with st.container(border=True):
        st.markdown("**Filter Data Rekap**")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        filter_col4, filter_col5, filter_col6 = st.columns(3)

        with filter_col1:
            selected_kelas = st.selectbox("Kode Kelas PAI", make_options(rekap["kode_kelas_pai"]))
        with filter_col2:
            selected_dosen = st.selectbox("Dosen Pengampu", make_options(rekap["dosen_pengampu"]))
        with filter_col3:
            selected_prodi = st.selectbox("Prodi", make_options(rekap["prodi"]))
        with filter_col4:
            selected_kelas_umum = st.selectbox("Kelas Umum", make_options(rekap["kelas_umum"]))
        with filter_col5:
            selected_status_nilai = st.selectbox("Status Nilai", ["Semua", "Sudah Ada Nilai", "Belum Ada Nilai"])
        with filter_col6:
            selected_status_validasi = st.selectbox("Status Validasi", ["Semua", "Valid", "Perlu Dicek"])

        keyword = st.text_input("Cari Nama/NIM", placeholder="Ketik nama atau NIM")

    filtered_rekap = rekap.copy()
    if selected_kelas != "Semua":
        filtered_rekap = filtered_rekap[filtered_rekap["kode_kelas_pai"].astype(str) == selected_kelas]
    if selected_dosen != "Semua":
        filtered_rekap = filtered_rekap[filtered_rekap["dosen_pengampu"].astype(str) == selected_dosen]
    if selected_prodi != "Semua":
        filtered_rekap = filtered_rekap[filtered_rekap["prodi"].astype(str) == selected_prodi]
    if selected_kelas_umum != "Semua":
        filtered_rekap = filtered_rekap[filtered_rekap["kelas_umum"].astype(str) == selected_kelas_umum]
    if selected_status_nilai != "Semua":
        filtered_rekap = filtered_rekap[filtered_rekap["status_nilai"] == selected_status_nilai]
    if selected_status_validasi != "Semua":
        filtered_rekap = filtered_rekap[filtered_rekap["status_validasi"] == selected_status_validasi]
    if keyword.strip():
        q = keyword.strip().lower()
        filtered_rekap = filtered_rekap[
            filtered_rekap["nim"].astype(str).str.lower().str.contains(q, na=False)
            | filtered_rekap["nama"].astype(str).str.lower().str.contains(q, na=False)
            | filtered_rekap["nama_nilai"].astype(str).str.lower().str.contains(q, na=False)
        ]

    st.caption(f"Menampilkan {format_number(len(filtered_rekap))} dari {format_number(len(rekap))} peserta.")
    return filtered_rekap


def render_upload_page() -> None:
    st.markdown('<div class="section-title">📤 Upload Data</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Masukkan File Peserta dan File Nilai, lalu klik tombol proses. Aplikasi tidak akan menganalisis otomatis sebelum tombol ditekan.</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**File Peserta wajib memiliki kolom:**")
            st.code("\n".join(PESERTA_REQUIRED_COLUMNS), language="text")
        with col2:
            st.markdown("**File Nilai wajib memiliki kolom:**")
            st.code("\n".join(NILAI_REQUIRED_COLUMNS), language="text")

        st.download_button(
            label="⬇️ Download Template Excel",
            data=create_template_excel(),
            file_name="template_rekap_tqq_akbar.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    upload_col1, upload_col2 = st.columns(2)
    with upload_col1:
        with st.container(border=True):
            st.markdown("### 📄 File Peserta")
            peserta_file = st.file_uploader(
                "Upload File Peserta",
                type=["xlsx", "xls", "csv"],
                help="File peserta berisi Nama, NIM, Prodi, Kelas Umum, Kode Kelas PAI, Dosen Pengampu.",
                key="peserta_file_upload",
            )
    with upload_col2:
        with st.container(border=True):
            st.markdown("### 📄 File Nilai")
            nilai_file = st.file_uploader(
                "Upload File Nilai",
                type=["xlsx", "xls", "csv"],
                help="File nilai berisi NAMA, NIM, PRESENSI, BACAAN, HAFALAN, EVALUASI, TOTAL NILAI, ABJAD.",
                key="nilai_file_upload",
            )

    if not peserta_file or not nilai_file:
        st.info("Silakan upload File Peserta dan File Nilai terlebih dahulu.")
        return

    try:
        raw_peserta = read_uploaded_file(peserta_file)
        raw_nilai = read_uploaded_file(nilai_file)
    except Exception as exc:
        st.error(f"Gagal membaca file: {exc}")
        return

    with st.expander("👀 Preview file asli", expanded=False):
        p1, p2 = st.columns(2)
        with p1:
            st.markdown("**Preview File Peserta**")
            st.dataframe(raw_peserta.head(20), use_container_width=True)
        with p2:
            st.markdown("**Preview File Nilai**")
            st.dataframe(raw_nilai.head(20), use_container_width=True)

    peserta_df, missing_peserta = standardize_dataframe(raw_peserta, PESERTA_COLUMN_ALIASES, "peserta")
    nilai_df, missing_nilai = standardize_dataframe(raw_nilai, NILAI_COLUMN_ALIASES, "nilai")

    if missing_peserta or missing_nilai:
        st.error("Ada kolom wajib yang belum ditemukan.")
        if missing_peserta:
            st.warning("Kolom yang belum ditemukan di File Peserta:")
            st.code("\n".join(missing_peserta), language="text")
        if missing_nilai:
            st.warning("Kolom yang belum ditemukan di File Nilai:")
            st.code("\n".join(missing_nilai), language="text")
        return

    file_signature = (
        peserta_file.name,
        getattr(peserta_file, "size", 0),
        nilai_file.name,
        getattr(nilai_file, "size", 0),
    )

    if st.session_state.get("last_file_signature") != file_signature:
        st.session_state["rekap_results"] = None
        st.session_state["last_file_signature"] = file_signature
        st.session_state["uploaded_file_names"] = (peserta_file.name, nilai_file.name)

    st.success("File berhasil dibaca dan format kolom wajib sudah sesuai.")

    btn_col1, btn_col2 = st.columns([2, 1])
    with btn_col1:
        process_clicked = st.button("🔍 Mulai Analisis / Rekap Data", type="primary", use_container_width=True)
    with btn_col2:
        st.caption("Proses akan menjalankan pencocokan NIM, validasi data, ringkasan, dan export.")

    if process_clicked:
        with st.spinner("Memproses rekap dan validasi data..."):
            st.session_state["rekap_results"] = process_rekap(peserta_df, nilai_df)
            st.session_state["uploaded_file_names"] = (peserta_file.name, nilai_file.name)
        st.success("Rekap selesai. Buka menu Dashboard, Hasil Rekap, Validasi Data, atau Export.")
        render_metric_cards(st.session_state["rekap_results"])


def render_rapikan_rekap_page() -> None:
    st.markdown('<div class="section-title">Mode Rapikan Hasil Rekap</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Mode ini digunakan untuk merapikan file hasil rekap yang sudah jadi. Sistem akan memisahkan data berdasarkan kombinasi Kode Kelas PAI dan Prodi, lalu mengurutkan isi sheet berdasarkan NIM.</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("**Upload file Excel hasil rekap**")
        rekap_file = st.file_uploader(
            "Upload file Excel hasil rekap",
            type=["xlsx", "xls"],
            help="Gunakan file hasil rekap yang sudah jadi. Mode ini tidak membutuhkan file peserta dan file nilai.",
            key="rapikan_rekap_file_upload",
        )

    if not rekap_file:
        st.session_state["rapikan_excel_bytes"] = None
        st.session_state["rapikan_sheet_preview"] = None
        st.info("Silakan upload file hasil rekap terlebih dahulu.")
        return

    file_signature = (rekap_file.name, getattr(rekap_file, "size", 0))
    if st.session_state.get("rapikan_file_signature") != file_signature:
        st.session_state["rapikan_file_signature"] = file_signature
        st.session_state["rapikan_excel_bytes"] = None
        st.session_state["rapikan_sheet_preview"] = None

    try:
        combined_rekap = read_rekap_file(rekap_file)
    except RekapRequiredColumnError as exc:
        st.error("Kolom wajib belum lengkap. Pastikan file memiliki kolom NIM, Prodi, dan Kode Kelas PAI.")
        st.caption(str(exc))
        return
    except Exception:
        st.error("File tidak dapat dibaca. Pastikan format file adalah Excel.")
        return

    if combined_rekap.empty:
        st.warning("Data rekap kosong atau tidak ditemukan.")
        return

    kelas_col = REKAP_INTERNAL_COLUMNS["kode_kelas_pai"]
    prodi_col = REKAP_INTERNAL_COLUMNS["prodi"]
    kelas_values = combined_rekap[kelas_col].apply(lambda value: "" if is_blank(value) else normalize_text(value))
    prodi_values = combined_rekap[prodi_col].apply(lambda value: "" if is_blank(value) else normalize_text(value))
    sheet_preview = build_rekap_kelas_prodi_preview(combined_rekap)

    st.success("File berhasil dibaca dan siap dirapikan.")

    st.markdown("**Ringkasan statistik**")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.metric("Total Data", format_number(len(combined_rekap)))
    with metric_col2:
        st.metric("Total Kode Kelas PAI", format_number(int(kelas_values[kelas_values.ne("")].nunique())))
    with metric_col3:
        st.metric("Total Prodi", format_number(int(prodi_values[prodi_values.ne("")].nunique())))
    with metric_col4:
        st.metric("Total Sheet", format_number(len(sheet_preview)))

    with st.container(border=True):
        st.markdown("**Preview data gabungan**")
        st.dataframe(drop_rekap_internal_columns(combined_rekap).head(100), use_container_width=True, height=360)

    with st.container(border=True):
        st.markdown("**Preview sheet yang akan dibuat**")
        st.dataframe(sheet_preview, use_container_width=True, height=320)

    process_clicked = st.button(
        "Proses Rapikan Rekap",
        type="primary",
        use_container_width=True,
    )

    if process_clicked:
        with st.spinner("Memproses file hasil rekap..."):
            st.session_state["rapikan_excel_bytes"] = export_rekap_by_kelas_prodi(combined_rekap)
            st.session_state["rapikan_sheet_preview"] = sheet_preview
        st.success("File hasil rekap berhasil dirapikan.")

    if st.session_state.get("rapikan_excel_bytes"):
        st.download_button(
            label="Download Excel Hasil Rapikan",
            data=st.session_state["rapikan_excel_bytes"],
            file_name="rekap_tqq_per_kode_kelas_dan_prodi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )


def render_charts(results: Dict[str, pd.DataFrame]) -> None:
    st.markdown('<div class="section-title">📈 Grafik Data Rekap</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Grafik membantu panitia melihat progres nilai, kelas prioritas, dan jenis masalah secara cepat.</div>',
        unsafe_allow_html=True,
    )

    rekap = results["rekap"]
    ringkasan = results["ringkasan"].copy()
    masalah_ringkasan = results["masalah_ringkasan"].copy()

    chart_col1, chart_col2 = st.columns([1, 1.45])

    with chart_col1:
        with st.container(border=True):
            st.markdown("**Komposisi Status Nilai**")
            status_df = pd.DataFrame({
                "Status": ["Sudah Ada Nilai", "Belum Ada Nilai"],
                "Jumlah": [
                    int((rekap["status_nilai"] == "Sudah Ada Nilai").sum()),
                    int((rekap["status_nilai"] == "Belum Ada Nilai").sum()),
                ],
            })
            fig_status = px.pie(
                status_df,
                names="Status",
                values="Jumlah",
                hole=0.58,
                color="Status",
                color_discrete_map={
                    "Sudah Ada Nilai": "#2563eb",
                    "Belum Ada Nilai": "#f59e0b",
                },
            )
            fig_status.update_traces(textposition="inside", textinfo="percent+label")
            fig_status.update_layout(
                height=350,
                margin=dict(l=10, r=10, t=20, b=10),
                showlegend=True,
                legend=dict(orientation="h", y=-0.12),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_status, use_container_width=True)

    with chart_col2:
        with st.container(border=True):
            st.markdown("**Progress Nilai per Kode Kelas PAI**")
            if ringkasan.empty:
                st.info("Belum ada data ringkasan kelas.")
            else:
                chart_ring = ringkasan.head(25).copy()
                plot_df = chart_ring.melt(
                    id_vars=["Kode Kelas PAI"],
                    value_vars=["Sudah Ada Nilai", "Belum Ada Nilai"],
                    var_name="Status",
                    value_name="Jumlah",
                )
                fig_bar = px.bar(
                    plot_df,
                    x="Kode Kelas PAI",
                    y="Jumlah",
                    color="Status",
                    barmode="stack",
                    color_discrete_map={
                        "Sudah Ada Nilai": "#2563eb",
                        "Belum Ada Nilai": "#f59e0b",
                    },
                )
                fig_bar.update_layout(
                    height=350,
                    margin=dict(l=10, r=10, t=20, b=10),
                    xaxis_title="Kode Kelas PAI",
                    yaxis_title="Jumlah Peserta",
                    legend=dict(orientation="h", y=-0.22),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_bar, use_container_width=True)

    chart_col3, chart_col4 = st.columns([1.15, 1])
    with chart_col3:
        with st.container(border=True):
            st.markdown("**Kelas dengan Belum Ada Nilai Terbanyak**")
            if ringkasan.empty:
                st.info("Belum ada data.")
            else:
                top_belum = ringkasan.sort_values("Belum Ada Nilai", ascending=False).head(12)
                fig_top = px.bar(
                    top_belum,
                    x="Belum Ada Nilai",
                    y="Kode Kelas PAI",
                    orientation="h",
                    text="Belum Ada Nilai",
                    color_discrete_sequence=["#0ea5e9"],
                )
                fig_top.update_layout(
                    height=360,
                    margin=dict(l=10, r=10, t=20, b=10),
                    xaxis_title="Jumlah Belum Ada Nilai",
                    yaxis_title="Kode Kelas PAI",
                    yaxis=dict(autorange="reversed"),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_top, use_container_width=True)

    with chart_col4:
        with st.container(border=True):
            st.markdown("**Jenis Masalah Terbanyak**")
            if masalah_ringkasan.empty:
                st.success("Tidak ada data bermasalah yang terdeteksi.")
            else:
                top_masalah = masalah_ringkasan.head(10).sort_values("Jumlah", ascending=True)
                fig_problem = px.bar(
                    top_masalah,
                    x="Jumlah",
                    y="Jenis Masalah",
                    orientation="h",
                    text="Jumlah",
                    color_discrete_sequence=["#1d4ed8"],
                )
                fig_problem.update_layout(
                    height=360,
                    margin=dict(l=10, r=10, t=20, b=10),
                    xaxis_title="Jumlah",
                    yaxis_title="",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig_problem, use_container_width=True)

def render_dashboard(results: Dict[str, pd.DataFrame]) -> None:
    st.markdown('<div class="section-title">📊 Dashboard Rekap</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Ringkasan kondisi rekap nilai TQQ Akbar berdasarkan file terakhir yang diproses.</div>', unsafe_allow_html=True)
    render_metric_cards(results)

    col1, col2 = st.columns([1.35, 1])
    with col1:
        with st.container(border=True):
            st.markdown("**Ringkasan per Kode Kelas PAI**")
            st.dataframe(results["ringkasan"], use_container_width=True, height=420)
    with col2:
        with st.container(border=True):
            st.markdown("**Ringkasan Masalah**")
            if results["masalah_ringkasan"].empty:
                st.success("Tidak ada data bermasalah yang terdeteksi.")
            else:
                st.dataframe(results["masalah_ringkasan"], use_container_width=True, height=420)


def render_rekap_page(results: Dict[str, pd.DataFrame]) -> None:
    st.markdown('<div class="section-title">📋 Hasil Rekap</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Gunakan filter untuk mengecek data per kelas, dosen, prodi, status nilai, atau status validasi.</div>', unsafe_allow_html=True)

    filtered_rekap = apply_filters(results["rekap"])
    tab1, tab2, tab3 = st.tabs(["Semua Rekap", "Sudah Ada Nilai", "Belum Ada Nilai"])
    with tab1:
        st.dataframe(reorder_and_rename(filtered_rekap), use_container_width=True, height=560)
    with tab2:
        sudah_filtered = filtered_rekap[filtered_rekap["status_nilai"] == "Sudah Ada Nilai"]
        st.dataframe(reorder_and_rename(sudah_filtered), use_container_width=True, height=560)
    with tab3:
        belum_filtered = filtered_rekap[filtered_rekap["status_nilai"] == "Belum Ada Nilai"]
        st.dataframe(reorder_and_rename(belum_filtered), use_container_width=True, height=560)


def render_validasi_page(results: Dict[str, pd.DataFrame]) -> None:
    st.markdown('<div class="section-title">🧪 Validasi Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Daftar masalah yang perlu dicek panitia sebelum hasil final dibagikan.</div>', unsafe_allow_html=True)

    data_bermasalah = results["data_bermasalah"]
    masalah_ringkasan = results["masalah_ringkasan"]

    range_text = ", ".join(
        [f"{config['label']} {config['min']:g}-{config['max']:g}" for config in SCORE_RANGE_CONFIG.values()]
    )
    st.info(f"Cek rentang nilai aktif: {range_text}.")

    if data_bermasalah.empty:
        st.success("Tidak ada data bermasalah yang terdeteksi.")
        return

    col1, col2 = st.columns([1, 2])
    with col1:
        with st.container(border=True):
            st.markdown("**Ringkasan Jenis Masalah**")
            st.dataframe(masalah_ringkasan, use_container_width=True, height=420)
    with col2:
        with st.container(border=True):
            st.markdown("**Detail Data Bermasalah**")
            st.dataframe(data_bermasalah, use_container_width=True, height=420)

    with st.container(border=True):
        st.markdown("**Peserta dengan Status Validasi Perlu Dicek**")
        st.dataframe(reorder_and_rename(results["perlu_dicek"]), use_container_width=True, height=420)


def render_export_page(results: Dict[str, pd.DataFrame]) -> None:
    st.markdown('<div class="section-title">⬇️ Export Hasil</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Export utama dibuat dalam satu file Excel dengan banyak sheet per Kode Kelas PAI. Setiap sheet berisi kolom final yang siap dibagikan.</div>',
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("**Format export final per sheet:**")
        st.code("Nama\nNIM\nProdi\nKelas Umum\nKode Kelas PAI\nDosen Pengampu\nPRESENSI\nBACAAN\nHAFALAN\nEVALUASI\nTOTAL NILAI\nABJAD", language="text")

    with st.container(border=True):
        st.markdown("**Preview sheet yang akan dibuat sebelum export:**")
        preview_sheet = build_export_sheet_preview(results)
        st.dataframe(preview_sheet, use_container_width=True, height=360)
        total_sheet = len(preview_sheet)
        total_perlu_dicek = int(preview_sheet["Perlu Dicek"].sum()) if not preview_sheet.empty else 0
        total_belum = int(preview_sheet["Belum Ada Nilai"].sum()) if not preview_sheet.empty else 0
        if total_perlu_dicek or total_belum:
            st.warning(
                f"Preview menemukan {total_sheet} sheet. Masih ada {format_number(total_perlu_dicek)} peserta perlu dicek dan {format_number(total_belum)} peserta belum ada nilai."
            )
        else:
            st.success(f"Preview menemukan {total_sheet} sheet dan semua data tampak aman untuk export.")

    export_col1, export_col2, export_col3, export_col4 = st.columns(4)
    with export_col1:
        st.download_button(
            label="📦 Excel Final Per Kode Kelas PAI",
            data=export_excel(results, include_per_kelas=True),
            file_name="hasil_rekap_tqq_akbar_per_kode_kelas_pai.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )
    with export_col2:
        st.download_button(
            label="📑 Laporan Validasi",
            data=export_laporan_validasi_excel(results),
            file_name="laporan_validasi_rekap_tqq.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with export_col3:
        st.download_button(
            label="🧪 Data Bermasalah",
            data=export_data_bermasalah_excel(results),
            file_name="data_bermasalah_rekap_tqq.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with export_col4:
        st.download_button(
            label="📄 Template Excel",
            data=create_template_excel(),
            file_name="template_rekap_tqq_akbar.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )


inject_custom_css()

if "rekap_results" not in st.session_state:
    st.session_state["rekap_results"] = None
if "uploaded_file_names" not in st.session_state:
    st.session_state["uploaded_file_names"] = None
if "rapikan_excel_bytes" not in st.session_state:
    st.session_state["rapikan_excel_bytes"] = None
if "rapikan_sheet_preview" not in st.session_state:
    st.session_state["rapikan_sheet_preview"] = None

with st.sidebar:
    st.markdown(
        """
        <div class="nav-brand">
            <div class="nav-title">TQQ Akbar UNESA</div>
            <div class="nav-subtitle">Satu halaman untuk upload, rekap, validasi, grafik, dan export.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sidebar-guide">
            <div class="sidebar-guide-title">Panduan Singkat</div>
            <ol>
                <li>Upload 2 file.</li>
                <li>Klik proses rekap.</li>
                <li>Cek grafik dan validasi.</li>
                <li>Export hasil Excel.</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("uploaded_file_names"):
        st.divider()
        peserta_name, nilai_name = st.session_state["uploaded_file_names"]
        st.caption("File terakhir diproses:")
        st.caption(f"Peserta: `{peserta_name}`")
        st.caption(f"Nilai: `{nilai_name}`")

st.sidebar.divider()
app_mode = st.sidebar.radio(
    "Mode Aplikasi",
    [MODE_REKAP, MODE_RAPIKAN],
    index=0,
    key="app_mode",
)
if app_mode == MODE_RAPIKAN:
    st.sidebar.caption("Mode ini hanya membutuhkan 1 file Excel hasil rekap.")

if app_mode == MODE_RAPIKAN:
    render_rapikan_rekap_page()
    st.stop()

render_hero()
render_process_steps(st.session_state.get("rekap_results") is not None)
render_upload_page()

results = st.session_state.get("rekap_results")
if results is None:
    st.markdown('<div class="section-title">📌 Menunggu Data Diproses</div>', unsafe_allow_html=True)
    st.info("Setelah File Peserta dan File Nilai diproses, dashboard, grafik, tabel rekap, validasi, dan export akan muncul otomatis di bawah halaman ini.")
else:
    st.divider()
    st.markdown('<div class="section-title">📊 Dashboard Ringkasan</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-caption">Ringkasan kondisi rekap nilai TQQ Akbar berdasarkan file terakhir yang diproses.</div>', unsafe_allow_html=True)
    render_metric_cards(results)

    render_charts(results)

    with st.expander("📋 Lihat dan Filter Hasil Rekap", expanded=True):
        render_rekap_page(results)

    with st.expander("🧪 Lihat Validasi Data Bermasalah", expanded=False):
        render_validasi_page(results)

    render_export_page(results)
