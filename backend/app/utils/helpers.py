"""Helper normalisasi dan pengurutan yang independen dari Streamlit."""

import re
from difflib import SequenceMatcher
from typing import Any, Tuple

import pandas as pd


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
