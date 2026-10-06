"""Logic mode Kehadiran: menambahkan keterangan hadir/tidak hadir ke file pembagian kelas."""

from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from backend.app.utils.helpers import (
    detect_column_mapping,
    is_blank,
    normalize_header,
    normalize_nim,
    normalize_text,
)

HADIR = "Hadir"
TIDAK_HADIR = "Tidak Hadir"
KOLOM_KEHADIRAN = "Keterangan Kehadiran"

KEHADIRAN_COLUMN_ALIASES: Dict[str, List[str]] = {
    "nim": ["NIM", "Nomor Induk Mahasiswa"],
    "status": ["Status", "Keterangan", "Kehadiran", "Status Kehadiran"],
}
KEHADIRAN_COLUMN_LABELS = {"nim": "NIM", "status": "Status"}

_HADIR_FILL = PatternFill("solid", fgColor="C6EFCE")
_HADIR_FONT = Font(color="006100")
_TIDAK_HADIR_FILL = PatternFill("solid", fgColor="FFC7CE")
_TIDAK_HADIR_FONT = Font(color="9C0006")


class KehadiranRequiredColumnError(ValueError):
    """Error khusus ketika file rekap kehadiran tidak memiliki kolom wajib."""


class KelasFileError(ValueError):
    """Error khusus ketika file pembagian kelas tidak bisa diproses."""


def normalize_status(value: Any) -> Optional[str]:
    """Kanonisasi status kehadiran. None bila isinya kosong atau tidak dikenali."""
    text = normalize_text(value).lower()
    if not text:
        return None
    if "tidak" in text or text in {"absen", "alpa", "alpha", "tidak hadir", "t"}:
        return TIDAK_HADIR
    if "hadir" in text or text in {"h", "present"}:
        return HADIR
    return None


def read_kehadiran_file(uploaded_file) -> Dict[str, str]:
    """Baca semua sheet rekap kehadiran menjadi kamus ``NIM -> Hadir/Tidak Hadir``.

    Jika satu NIM muncul lebih dari sekali, ``Hadir`` didahulukan.
    """
    filename = uploaded_file.name.lower()
    if not filename.endswith((".xlsx", ".xls")):
        raise ValueError("Format file tidak didukung. Gunakan .xlsx atau .xls")

    uploaded_file.seek(0)
    sheets = pd.read_excel(uploaded_file, sheet_name=None, dtype=str)
    kehadiran: Dict[str, str] = {}
    for sheet_name, sheet_df in sheets.items():
        sheet_df = sheet_df.dropna(how="all")
        if sheet_df.empty:
            continue
        mapping, missing = detect_column_mapping(sheet_df, KEHADIRAN_COLUMN_ALIASES)
        if missing:
            labels = ", ".join(KEHADIRAN_COLUMN_LABELS[col] for col in missing)
            raise KehadiranRequiredColumnError(f"Sheet '{sheet_name}' belum memiliki kolom: {labels}")
        for nim_value, status_value in zip(sheet_df[mapping["nim"]], sheet_df[mapping["status"]]):
            nim = normalize_nim(nim_value)
            status = normalize_status(status_value)
            if not nim or status is None:
                continue
            if kehadiran.get(nim) != HADIR:
                kehadiran[nim] = status
    return kehadiran


def _find_nim_column(row_values: Tuple[Any, ...]) -> Optional[int]:
    for index, value in enumerate(row_values, start=1):
        if not is_blank(value) and normalize_header(value) == "nim":
            return index
    return None


def _last_filled_column(row_values: Tuple[Any, ...]) -> int:
    last = 0
    for index, value in enumerate(row_values, start=1):
        if not is_blank(value):
            last = index
    return last


def _style_status_cell(cell, status: str) -> None:
    if status == HADIR:
        cell.fill, cell.font = _HADIR_FILL, _HADIR_FONT
    else:
        cell.fill, cell.font = _TIDAK_HADIR_FILL, _TIDAK_HADIR_FONT
    cell.alignment = Alignment(horizontal="center")


def add_kehadiran_to_kelas(
    kelas_bytes: bytes,
    kehadiran: Dict[str, str],
) -> Tuple[bytes, pd.DataFrame, pd.DataFrame]:
    """Tambahkan kolom ``Keterangan Kehadiran`` di sisi kanan tiap tabel peserta.

    Struktur file pembagian kelas (sheet, info tentor, kolom lama) dipertahankan.
    NIM yang tidak ada di rekap kehadiran dihitung ``Tidak Hadir``.

    Returns:
        (bytes Excel hasil, ringkasan per kelas, daftar peserta yang tidak ada di rekap)
    """
    workbook = load_workbook(BytesIO(kelas_bytes))
    ringkasan_rows: List[Dict[str, Any]] = []
    tidak_ada_rows: List[Dict[str, Any]] = []

    for worksheet in workbook.worksheets:
        counts = {HADIR: 0, TIDAK_HADIR: 0, "tidak_ada_di_rekap": 0}
        nim_col: Optional[int] = None
        status_col = 0
        nama_col: Optional[int] = None
        header_row = 0

        for row_number, row in enumerate(list(worksheet.iter_rows(values_only=True)), start=1):
            found_nim_col = _find_nim_column(row)
            if found_nim_col is not None:
                # Baris header tabel peserta; bisa ada lebih dari satu tabel per sheet.
                nim_col = found_nim_col
                header_row = row_number
                status_col = _last_filled_column(row) + 1
                nama_col = next(
                    (i for i, v in enumerate(row, start=1) if not is_blank(v) and normalize_header(v) == "nama"),
                    None,
                )
                header_cell = worksheet.cell(row=row_number, column=status_col, value=KOLOM_KEHADIRAN)
                source_header = worksheet.cell(row=row_number, column=status_col - 1)
                if source_header.has_style:
                    header_cell._style = source_header._style
                continue

            if nim_col is None or row_number <= header_row:
                continue
            nim = normalize_nim(row[nim_col - 1] if nim_col - 1 < len(row) else None)
            if not nim:
                continue

            status = kehadiran.get(nim)
            if status is None:
                status = TIDAK_HADIR
                counts["tidak_ada_di_rekap"] += 1
                nama = row[nama_col - 1] if nama_col and nama_col - 1 < len(row) else None
                tidak_ada_rows.append({"Kelas": worksheet.title, "Nama": normalize_text(nama), "NIM": nim})
            counts[status] += 1

            cell = worksheet.cell(row=row_number, column=status_col, value=status)
            source_cell = worksheet.cell(row=row_number, column=status_col - 1)
            if source_cell.has_style:
                cell._style = source_cell._style
            _style_status_cell(cell, status)

        if header_row:
            worksheet.column_dimensions[get_column_letter(status_col)].width = 22
            total = counts[HADIR] + counts[TIDAK_HADIR]
            ringkasan_rows.append(
                {
                    "Kelas": worksheet.title,
                    "Total Mahasiswa": total,
                    "Hadir": counts[HADIR],
                    "Tidak Hadir": counts[TIDAK_HADIR],
                    "Tidak Ada di Rekap": counts["tidak_ada_di_rekap"],
                    "% Hadir": round(counts[HADIR] / total * 100, 1) if total else 0.0,
                }
            )

    if not ringkasan_rows:
        raise KelasFileError("Tidak ditemukan kolom 'NIM' di file pembagian kelas.")

    output = BytesIO()
    workbook.save(output)
    return output.getvalue(), pd.DataFrame(ringkasan_rows), pd.DataFrame(tidak_ada_rows, columns=["Kelas", "Nama", "NIM"])


def build_kehadiran_summary(ringkasan: pd.DataFrame) -> Dict[str, Any]:
    total = int(ringkasan["Total Mahasiswa"].sum())
    hadir = int(ringkasan["Hadir"].sum())
    return {
        "total_mahasiswa": total,
        "total_hadir": hadir,
        "total_tidak_hadir": int(ringkasan["Tidak Hadir"].sum()),
        "total_tidak_ada_di_rekap": int(ringkasan["Tidak Ada di Rekap"].sum()),
        "total_kelas": int(len(ringkasan)),
        "persentase_hadir": round(hadir / total * 100, 1) if total else 0.0,
    }
