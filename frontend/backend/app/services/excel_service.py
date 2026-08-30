"""Export Excel TQQ tanpa ketergantungan Streamlit."""

import zipfile
from io import BytesIO
from typing import Dict

import pandas as pd

from backend.app.core.config import (
    EXPORT_PER_KELAS_COLUMN_LABELS,
    EXPORT_PER_KELAS_COLUMNS,
    FINAL_COLUMN_LABELS,
    FINAL_COLUMNS,
    NILAI_REQUIRED_COLUMNS,
    PESERTA_REQUIRED_COLUMNS,
    SCORE_RANGE_CONFIG,
)
from backend.app.utils.helpers import is_blank, safe_filename_part, safe_sheet_name


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


def export_excel(results: Dict[str, pd.DataFrame], include_per_kelas: bool = True) -> bytes:
    """Export utama: 1 file Excel berisi banyak sheet per Kode Kelas PAI."""
    output = BytesIO()
    rekap = results["rekap"].copy()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        if rekap.empty:
            pd.DataFrame(columns=list(EXPORT_PER_KELAS_COLUMN_LABELS.values())).to_excel(writer, sheet_name="Data Kosong", index=False)
        else:
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
        return pd.DataFrame(columns=["Kode Kelas PAI", "Nama Sheet", "Jumlah Peserta", "Sudah Ada Nilai", "Belum Ada Nilai", "Perlu Dicek", "Status Export"])

    rows = []
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
            "Kode Kelas PAI": kelas_label, "Nama Sheet": sheet_name, "Jumlah Peserta": int(len(group)),
            "Sudah Ada Nilai": int((group["status_nilai"] == "Sudah Ada Nilai").sum()),
            "Belum Ada Nilai": belum_ada, "Perlu Dicek": perlu_dicek,
            "Status Export": "Perlu dicek" if perlu_dicek or belum_ada else "Aman",
        })
    return pd.DataFrame(rows)


def export_laporan_validasi_excel(results: Dict[str, pd.DataFrame]) -> bytes:
    output = BytesIO()
    data_bermasalah = results["data_bermasalah"].copy()
    preview_sheet = build_export_sheet_preview(results)
    rentang_df = pd.DataFrame([{"Kolom": config["label"], "Nilai Minimum": config["min"], "Nilai Maksimum": config["max"], "Keterangan": "Nilai kosong dicek sebagai masalah terpisah; validasi rentang hanya untuk nilai yang terisi."} for config in SCORE_RANGE_CONFIG.values()])
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
