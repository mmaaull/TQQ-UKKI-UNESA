"""Helper normalisasi dan pengurutan yang independen dari Streamlit."""

import re
from difflib import SequenceMatcher
from typing import Any, Dict, List, Tuple

import pandas as pd


def normalize_header(value: Any) -> str:
    text = str(value).strip().lower()
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def detect_column_mapping(
    df: pd.DataFrame,
    aliases: Dict[str, List[str]],
) -> Tuple[Dict[str, str], List[str]]:
    """Mendeteksi kolom input berdasarkan alias tanpa mengubah DataFrame."""
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


def normalize_gender(value: Any) -> str:
    """Kanonisasi jenis kelamin ke 'L'/'P', string kosong bila tidak dikenali."""
    if pd.isna(value):
        return ""
    text = str(value).strip().upper()
    if text in {"L", "LAKI-LAKI", "LAKI LAKI", "LAKI", "PRIA", "M", "MALE"}:
        return "L"
    if text in {"P", "PEREMPUAN", "WANITA", "F", "FEMALE"}:
        return "P"
    return ""


def read_all_sheets(uploaded_file) -> pd.DataFrame:
    """Membaca seluruh sheet Excel/CSV lalu menggabungkan baris yang tidak kosong."""
    filename = uploaded_file.name.lower()
    if filename.endswith(".csv"):
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, dtype=str)
    if not filename.endswith((".xlsx", ".xls")):
        raise ValueError("Format file tidak didukung. Gunakan .xlsx, .xls, atau .csv")

    uploaded_file.seek(0)
    sheets = pd.read_excel(uploaded_file, sheet_name=None, dtype=str)
    frames = [sheet.dropna(how="all") for sheet in sheets.values()]
    frames = [frame for frame in frames if not frame.empty]
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True, sort=False)


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
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


def safe_sheet_name(name: str) -> str:
    cleaned = re.sub(r"[\[\]\:\*\?\/\\\\]", "-", str(name))
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


def clean_sheet_name(name: str, existing_names: set[str]) -> str:
    """Membersihkan nama sheet Excel, memotong ke 31 karakter, dan menjaga tetap unik."""
    cleaned = re.sub(r"[\:\?\/\\\\\*\[\]]", " ", str(name))
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


def split_evenly(n_items: int, n_groups: int) -> List[int]:
    """Bagi ``n_items`` ke ``n_groups`` kelompok serata mungkin (selisih antar kelompok maks. 1)."""
    base, remainder = divmod(n_items, n_groups)
    return [base + 1 if i < remainder else base for i in range(n_groups)]
