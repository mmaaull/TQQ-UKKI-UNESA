"""Verifikasi hasil logic Streamlit terhadap fixture baseline."""

from __future__ import annotations

import json
import sys
from io import BytesIO
from pathlib import Path

import pandas as pd

from _app_logic import PROJECT_ROOT, load_app_logic
from generate_baseline import EXPECTED_DIR, ensure_input_fixtures, load_results, make_summary


CSV_BASELINES = {
    "Hasil rekap": ("hasil_rekap.csv", "rekap"),
    "Data bermasalah": ("data_bermasalah.csv", "data_bermasalah"),
    "Ringkasan kelas": ("ringkasan_kelas.csv", "ringkasan"),
    "Ringkasan masalah": ("ringkasan_masalah.csv", "masalah_ringkasan"),
}

EXPORT_BASELINES = {
    "Export final": ("export_final.xlsx", "export_excel"),
    "Export validasi": ("export_validasi.xlsx", "export_laporan_validasi_excel"),
    "Export data bermasalah": ("export_data_bermasalah.xlsx", "export_data_bermasalah_excel"),
}


def comparable_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalisasi hanya untuk pembandingan, tanpa mengubah hasil production."""
    normalized = df.reset_index(drop=True).copy().fillna("")
    return normalized.astype(str)


def compare_dataframe(expected: pd.DataFrame, actual: pd.DataFrame) -> list[str]:
    expected = comparable_dataframe(expected)
    actual = comparable_dataframe(actual)
    messages: list[str] = []
    if list(expected.columns) != list(actual.columns):
        messages.append(f"Kolom expected: {list(expected.columns)}")
        messages.append(f"Kolom actual: {list(actual.columns)}")
        return messages
    if len(expected) != len(actual):
        messages.append(f"Jumlah row expected: {len(expected)}")
        messages.append(f"Jumlah row actual: {len(actual)}")
    if expected.equals(actual):
        return []

    if len(expected) == len(actual):
        differences = expected.ne(actual)
        changed_columns = differences.any()
        columns = list(changed_columns[changed_columns].index)
        messages.append(f"Kolom berbeda: {columns}")
        if columns:
            row_index = int(differences[columns].any(axis=1).idxmax())
            messages.append(
                f"Contoh perbedaan row {row_index}: expected={expected.loc[row_index, columns].to_dict()}, "
                f"actual={actual.loc[row_index, columns].to_dict()}"
            )
    return messages or ["Isi DataFrame berbeda."]


def compare_excel(expected_path: Path, actual_bytes: bytes) -> list[str]:
    with pd.ExcelFile(expected_path) as expected_book, pd.ExcelFile(BytesIO(actual_bytes)) as actual_book:
        if expected_book.sheet_names != actual_book.sheet_names:
            return [
                f"Sheet expected: {expected_book.sheet_names}",
                f"Sheet actual: {actual_book.sheet_names}",
            ]
        for sheet_name in expected_book.sheet_names:
            expected = pd.read_excel(expected_book, sheet_name=sheet_name, dtype=str, keep_default_na=False)
            actual = pd.read_excel(actual_book, sheet_name=sheet_name, dtype=str, keep_default_na=False)
            differences = compare_dataframe(expected, actual)
            if differences:
                return [f"Sheet berbeda: {sheet_name}", *differences]
    return []


def report(label: str, differences: list[str]) -> bool:
    if not differences:
        print(f"[PASS] {label} sama")
        return True
    print(f"[FAIL] {label} berbeda")
    for detail in differences:
        print(f"  {detail}")
    return False


def main() -> int:
    ensure_input_fixtures()
    required = [EXPECTED_DIR / "summary.json"]
    required.extend(EXPECTED_DIR / filename for filename, _ in CSV_BASELINES.values())
    required.extend(EXPECTED_DIR / filename for filename, _ in EXPORT_BASELINES.values())
    missing = [path.relative_to(PROJECT_ROOT) for path in required if not path.exists()]
    if missing:
        print("[FAIL] Baseline belum lengkap. Jalankan generate_baseline.py terlebih dahulu.")
        for path in missing:
            print(f"  Tidak ditemukan: {path}")
        return 1

    results = load_results()
    app = load_app_logic()
    passed = True

    expected_summary = json.loads((EXPECTED_DIR / "summary.json").read_text(encoding="utf-8"))
    actual_summary = make_summary(results)
    passed &= report(
        "Summary",
        [] if expected_summary == actual_summary else [
            f"Expected: {expected_summary}", f"Actual: {actual_summary}"
        ],
    )

    for label, (filename, result_key) in CSV_BASELINES.items():
        expected = pd.read_csv(EXPECTED_DIR / filename, dtype=str, keep_default_na=False)
        passed &= report(label, compare_dataframe(expected, results[result_key]))

    for label, (filename, function_name) in EXPORT_BASELINES.items():
        export_function = getattr(app, function_name)
        passed &= report(label, compare_excel(EXPECTED_DIR / filename, export_function(results)))

    print()
    print("Baseline verification PASSED." if passed else "Baseline verification FAILED.")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
