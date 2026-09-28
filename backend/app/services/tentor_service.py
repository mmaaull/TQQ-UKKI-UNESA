"""Logic mode Pembagian Tentor dari hasil Rekap Jilid tanpa ketergantungan UI.

Input file adalah hasil unduhan Mode Rekap Jilid (sheet per kombinasi Jilid +
Jenis Kelamin). Jumlah tentor Laki-laki dan Perempuan diinput sebagai total
per jenis kelamin, lalu dialokasikan ke tiap Jilid secara proporsional
terhadap jumlah peserta (metode largest remainder) sehingga tiap kelas Jilid
tetap dipegang oleh tentor yang tidak bercampur jilid lain. Peserta pada tiap
kelas Jilid kemudian dibagi serata mungkin ke jumlah tentor yang dialokasikan.
"""

from io import BytesIO
from typing import Any, Dict, List, Tuple

import pandas as pd

from backend.app.core.config import (
    JILID_GENDER_SHEET_LABELS,
    JILID_LABELS,
    TENTOR_OUTPUT_COLUMNS,
    jilid_sheet_name,
)
from backend.app.utils.helpers import clean_sheet_name, split_evenly

RINGKASAN_SHEET_NAME = "Ringkasan Tentor"


class TentorRequiredDataError(ValueError):
    """Error ketika file yang diupload bukan hasil Rekap Jilid yang valid."""


class TentorAllocationError(ValueError):
    """Error ketika jumlah tentor yang diinput tidak sesuai dengan data peserta."""


def read_jilid_recap_file(uploaded_file) -> Dict[Tuple[str, str], pd.DataFrame]:
    """Baca file hasil unduhan Rekap Jilid, kembalikan peserta per (Jilid, kode gender)."""
    filename = uploaded_file.name.lower()
    if not filename.endswith((".xlsx", ".xls")):
        raise ValueError("Format file tidak didukung. Gunakan .xlsx atau .xls")

    uploaded_file.seek(0)
    sheets = pd.read_excel(uploaded_file, sheet_name=None, dtype=str)

    expected_sheet_names = {
        jilid_sheet_name(jilid_label, gender_label): (jilid_label, gender_code)
        for jilid_label in JILID_LABELS
        for gender_code, gender_label in JILID_GENDER_SHEET_LABELS
    }

    groups: Dict[Tuple[str, str], pd.DataFrame] = {}
    for sheet_name, sheet_df in sheets.items():
        key = expected_sheet_names.get(str(sheet_name).strip())
        if key is None:
            continue
        cleaned = sheet_df.dropna(how="all")
        if cleaned.empty:
            continue
        missing_columns = [col for col in TENTOR_OUTPUT_COLUMNS if col not in cleaned.columns]
        if missing_columns:
            raise TentorRequiredDataError(
                f"Sheet '{sheet_name}' tidak memiliki kolom: {', '.join(missing_columns)}. "
                "Pastikan file yang diupload adalah hasil unduhan Rekap Jilid."
            )
        groups[key] = cleaned[TENTOR_OUTPUT_COLUMNS].reset_index(drop=True)

    if not groups:
        raise TentorRequiredDataError(
            "File tidak berisi sheet hasil Rekap Jilid yang dikenali (contoh: "
            "'Jilid 1 - Laki-laki'). Upload file hasil unduhan Rekap Jilid."
        )
    return groups


def allocate_tentor_counts(counts: Dict[str, int], total_tentor: int) -> Dict[str, int]:
    """Bagi total tentor ke tiap kelompok (Jilid) proporsional ke jumlah peserta.

    Tiap kelompok berisi peserta dijamin mendapat minimal 1 tentor; sisa kuota
    dibagi proporsional dengan metode largest remainder (Hamilton) sehingga
    totalnya selalu tepat sama dengan ``total_tentor``.
    """
    active = {label: count for label, count in counts.items() if count > 0}
    if not active:
        return {label: 0 for label in counts}
    if total_tentor < len(active):
        raise TentorAllocationError(
            f"Jumlah tentor ({total_tentor}) kurang dari jumlah kelas Jilid berisi peserta "
            f"({len(active)}). Minimal {len(active)} tentor agar tiap kelas Jilid ada tentornya."
        )

    remaining_pool = total_tentor - len(active)
    total_peserta = sum(active.values())
    quotas = {label: remaining_pool * count / total_peserta for label, count in active.items()}
    extra = {label: int(quota) for label, quota in quotas.items()}
    leftover = remaining_pool - sum(extra.values())

    if leftover > 0:
        order = sorted(
            active.keys(),
            key=lambda label: (quotas[label] - int(quotas[label]), active[label]),
            reverse=True,
        )
        for label in order[:leftover]:
            extra[label] += 1

    allocation = {label: 1 + extra[label] for label in active}
    return {label: allocation.get(label, 0) for label in counts}


def build_tentor_distribution(
    jilid_groups: Dict[Tuple[str, str], pd.DataFrame],
    jumlah_tentor_laki_laki: int,
    jumlah_tentor_perempuan: int,
) -> Dict[str, Any]:
    """Bagi peserta tiap kelas Jilid ke jumlah tentor yang diinput per jenis kelamin."""
    gender_totals = {"L": jumlah_tentor_laki_laki, "P": jumlah_tentor_perempuan}
    gender_labels = dict(JILID_GENDER_SHEET_LABELS)

    tentor_sheets: Dict[str, pd.DataFrame] = {}
    ringkasan_rows: List[Dict[str, Any]] = []
    existing_sheet_names: set[str] = {RINGKASAN_SHEET_NAME}

    for gender_code, total_tentor in gender_totals.items():
        gender_label = gender_labels[gender_code]
        counts = {
            jilid_label: len(jilid_groups.get((jilid_label, gender_code), pd.DataFrame()))
            for jilid_label in JILID_LABELS
        }
        total_peserta_gender = sum(counts.values())

        if total_peserta_gender == 0:
            if total_tentor > 0:
                raise TentorAllocationError(
                    f"Tidak ada peserta {gender_label} di file ini, tapi jumlah tentor "
                    f"{gender_label} diisi {total_tentor}."
                )
            continue

        if total_tentor <= 0:
            raise TentorAllocationError(
                f"Jumlah tentor {gender_label} harus diisi minimal 1 "
                f"(ada {total_peserta_gender} peserta {gender_label})."
            )

        allocation = allocate_tentor_counts(counts, total_tentor)

        for jilid_label in JILID_LABELS:
            jumlah_tentor_kelas = allocation.get(jilid_label, 0)
            if jumlah_tentor_kelas == 0:
                continue
            peserta = jilid_groups[(jilid_label, gender_code)]
            chunk_sizes = split_evenly(len(peserta), jumlah_tentor_kelas)

            start = 0
            for tentor_index, chunk_size in enumerate(chunk_sizes, start=1):
                chunk = peserta.iloc[start : start + chunk_size].reset_index(drop=True)
                start += chunk_size
                sheet_name = clean_sheet_name(
                    f"{jilid_label} - {gender_label} - Tentor {tentor_index}",
                    existing_sheet_names,
                )
                tentor_sheets[sheet_name] = chunk
                ringkasan_rows.append({
                    "Jilid": jilid_label,
                    "Jenis Kelamin": gender_label,
                    "Tentor": f"Tentor {tentor_index}",
                    "Nama Sheet": sheet_name,
                    "Jumlah Peserta": int(chunk_size),
                })

    if not tentor_sheets:
        raise TentorRequiredDataError("Tidak ada peserta yang bisa dibagi ke tentor dari file ini.")

    ringkasan = pd.DataFrame(
        ringkasan_rows,
        columns=["Jilid", "Jenis Kelamin", "Tentor", "Nama Sheet", "Jumlah Peserta"],
    )

    summary = {
        "total_peserta": int(sum(row["Jumlah Peserta"] for row in ringkasan_rows)),
        "total_tentor": int(len(ringkasan_rows)),
        "total_tentor_laki_laki": int(
            sum(1 for row in ringkasan_rows if row["Jenis Kelamin"] == gender_labels["L"])
        ),
        "total_tentor_perempuan": int(
            sum(1 for row in ringkasan_rows if row["Jenis Kelamin"] == gender_labels["P"])
        ),
    }

    return {"tentor_sheets": tentor_sheets, "ringkasan": ringkasan, "summary": summary}


def export_tentor_excel(tentor_sheets: Dict[str, pd.DataFrame], ringkasan: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        ringkasan.to_excel(writer, sheet_name=RINGKASAN_SHEET_NAME, index=False)
        for sheet_name, group in tentor_sheets.items():
            group.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()
