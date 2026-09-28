"""Logic mode Rapikan Hasil Rekap tanpa ketergantungan Streamlit."""

from io import BytesIO
from typing import Any, Dict, List, Tuple

import pandas as pd

from backend.app.core.config import (
    REKAP_COLUMN_ALIASES,
    REKAP_INTERNAL_COLUMNS,
    REKAP_REQUIRED_COLUMN_LABELS,
)
from backend.app.utils.helpers import (
    clean_sheet_name,
    detect_column_mapping,
    is_blank,
    natural_sort_kelas_key,
    normalize_nim,
    normalize_text,
)


class RekapRequiredColumnError(ValueError):
    """Error khusus ketika file hasil rekap tidak memiliki kolom wajib."""


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


def sort_rekap_group_by_nim(group: pd.DataFrame) -> pd.DataFrame:
    sorted_group = group.copy()
    nim_col = REKAP_INTERNAL_COLUMNS["nim"]
    sorted_group["_rekap_sort_nim_text"] = sorted_group[nim_col].apply(normalize_nim)
    sorted_group["_rekap_sort_nim_number"] = pd.to_numeric(sorted_group["_rekap_sort_nim_text"], errors="coerce")
    sorted_group["_rekap_sort_nim_is_text"] = sorted_group["_rekap_sort_nim_number"].isna()
    sorted_group = sorted_group.sort_values(
        by=["_rekap_sort_nim_is_text", "_rekap_sort_nim_number", "_rekap_sort_nim_text"],
        ascending=True, na_position="last", kind="mergesort",
    )
    return sorted_group.drop(columns=["_rekap_sort_nim_text", "_rekap_sort_nim_number", "_rekap_sort_nim_is_text"], errors="ignore")


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
        rows.append({"Kode Kelas PAI": kelas_label, "Prodi": prodi_label, "Nama Sheet": clean_sheet_name(f"{kelas_label} - {prodi_label}", existing_names), "Jumlah Data": int(len(group))})
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
