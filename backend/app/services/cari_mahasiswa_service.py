"""Logic pencarian mahasiswa lintas sheet dan lintas file Excel.

Format file tidak dikunci ke satu template: tiap sheet dipindai untuk mencari
baris header (yang memuat kolom NIM dan/atau Nama), baris di atasnya dibaca
sebagai info sheet (mis. "Tentor: ...", "Link Grup WA: ..."), dan semua kolom
lain di tabel ikut disimpan apa adanya. Hasilnya daftar datar mahasiswa yang
bisa dicari berdasarkan NIM dan Nama tanpa membuka sheet satu per satu.
"""

from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from backend.app.utils.helpers import is_blank, normalize_header, normalize_nim, normalize_text

NIM_HEADERS = {"nim", "npm", "nomor induk mahasiswa", "no induk mahasiswa", "nomor induk", "no induk"}
NAMA_HEADERS = {
    "nama",
    "nama mahasiswa",
    "nama lengkap",
    "nama peserta",
    "nama mhs",
    "name",
}
# Kolom nomor urut tidak berguna untuk ditampilkan di hasil pencarian.
SKIPPED_HEADERS = {"no", "no.", "nomor", "nomor urut", "#"}
INFO_LABEL_MAX_LENGTH = 40


class KelasIndexError(ValueError):
    """Error ketika file tidak berisi tabel mahasiswa yang bisa dicari."""


def _header_columns(row: Tuple[Any, ...]) -> Optional[Dict[str, Any]]:
    """Kenali baris header: harus punya kolom NIM atau Nama (cocok persis dengan alias)."""
    nim_col: Optional[int] = None
    nama_col: Optional[int] = None
    filled = 0
    for index, value in enumerate(row):
        if is_blank(value):
            continue
        filled += 1
        header = normalize_header(value)
        if nim_col is None and header in NIM_HEADERS:
            nim_col = index
        elif nama_col is None and header in NAMA_HEADERS:
            nama_col = index
    if (nim_col is None and nama_col is None) or filled < 2:
        return None
    extras = [
        (index, normalize_text(value))
        for index, value in enumerate(row)
        if index not in (nim_col, nama_col)
        and not is_blank(value)
        and normalize_header(value) not in SKIPPED_HEADERS
    ]
    return {"nim": nim_col, "nama": nama_col, "extras": extras}


def _cell_text(row: Tuple[Any, ...], index: Optional[int]) -> str:
    if index is None or index >= len(row):
        return ""
    return "" if is_blank(row[index]) else normalize_text(row[index])


def _read_info_line(row: Tuple[Any, ...], info: Dict[str, str]) -> None:
    """Baris di atas tabel: 'Label: isi' disimpan per label, selain itu masuk 'Info'."""
    texts = [normalize_text(value) for value in row if not is_blank(value)]
    if not texts:
        return
    text = texts[0]
    label, separator, rest = text.partition(":")
    if separator and rest.strip() and len(label.strip()) <= INFO_LABEL_MAX_LENGTH:
        info[label.strip()] = rest.strip()
    else:
        info["Info"] = f"{info['Info']} | {text}" if "Info" in info else text


def _read_sheet(
    sheet_name: str, raw: pd.DataFrame, source: str
) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
    rows: List[Dict[str, Any]] = []
    data_columns: List[str] = []
    info: Dict[str, str] = {}
    header: Optional[Dict[str, Any]] = None
    info_columns: List[str] = []

    for values in raw.itertuples(index=False, name=None):
        found = _header_columns(values)
        if found is not None:
            header = found
            continue

        if header is None:
            _read_info_line(values, info)
            continue

        nim = normalize_nim(_cell_text(values, header["nim"]))
        nama = _cell_text(values, header["nama"])
        if not nim and not nama:
            continue

        data: Dict[str, str] = {}
        for index, label in header["extras"]:
            value = _cell_text(values, index)
            if value:
                data[label] = value
                if label not in data_columns:
                    data_columns.append(label)
        rows.append(
            {"sumber": source, "sheet": sheet_name, "nim": nim, "nama": nama, "data": data, "info": dict(info)}
        )

    for label in info:
        if any(label in row["info"] for row in rows):
            info_columns.append(label)
    return rows, data_columns, info_columns


def build_kelas_index(files: List[Tuple[str, bytes]]) -> Dict[str, Any]:
    """Baca semua sheet dari satu atau lebih file Excel menjadi daftar mahasiswa."""
    students: List[Dict[str, Any]] = []
    data_columns: List[str] = []
    info_columns: List[str] = []
    sheet_count = 0

    for filename, contents in files:
        try:
            sheets = pd.read_excel(BytesIO(contents), sheet_name=None, header=None, dtype=str)
        except Exception as exc:
            raise KelasIndexError(f"{filename} tidak dapat dibaca sebagai file Excel: {exc}") from exc

        for sheet_name, raw in sheets.items():
            rows, sheet_data_columns, sheet_info_columns = _read_sheet(str(sheet_name), raw, filename)
            if not rows:
                continue
            sheet_count += 1
            students.extend(rows)
            data_columns.extend(c for c in sheet_data_columns if c not in data_columns)
            info_columns.extend(c for c in sheet_info_columns if c not in info_columns)

    if not students:
        raise KelasIndexError(
            "Tidak ditemukan tabel mahasiswa. Pastikan ada baris header dengan kolom NIM dan/atau Nama."
        )

    return {
        "summary": {
            "total_mahasiswa": len(students),
            "total_sheet": sheet_count,
            "total_file": len(files),
        },
        "data_columns": data_columns,
        "info_columns": info_columns,
        "mahasiswa": students,
    }
