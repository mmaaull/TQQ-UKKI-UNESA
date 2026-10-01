"""Logic mode Rekap Pembagian Kelas Jilid tanpa ketergantungan UI.

File master (data keseluruhan peserta) menjadi acuan Nama, Jenis Kelamin,
Kelas PAI, dan Program Studi karena file penilaian tashih tidak memiliki
kolom jenis kelamin. Kelas Jilid dihitung ulang oleh sistem dari Total Nilai
di file penilaian (bukan dari kolom Jilid manual bila ada), lalu hasilnya
dipisah per Jilid (1-4) dan per jenis kelamin.

File master berisi peserta dari SEMUA gelombang tes tashih sekaligus,
sedangkan file penilaian yang diupload hanya berisi 1 gelombang. Supaya
peserta gelombang lain (yang belum waktunya direkap) tidak ikut tertarik,
sistem memakai Kelas PAI sebagai penanda gelombang: peserta master yang
Kelas PAI-nya sudah muncul di file penilaian ini tapi NIM-nya sendiri tidak
ada, dianggap "tidak ikut tes gelombang ini" dan otomatis dimasukkan ke
Jilid 1. Peserta di Kelas PAI yang sama sekali belum tersentuh file
penilaian ini (kemungkinan besar gelombang lain) tidak disertakan sama
sekali dalam rekap.
"""

from collections import defaultdict
from difflib import SequenceMatcher
from io import BytesIO
from typing import Any, Dict, List, Tuple

import pandas as pd

from backend.app.core.config import (
    JILID_AUTO_ASSIGN_NOTE,
    JILID_EMPTY_SCORE_NOTE,
    JILID_GENDER_SHEET_LABELS,
    JILID_LABELS,
    JILID_NAME_SIMILARITY_THRESHOLD,
    JILID_OUTPUT_COLUMN_LABELS,
    JILID_OUTPUT_COLUMNS,
    JILID_PROBLEM_GENDER_UNKNOWN,
    JILID_PROBLEM_NAME_MISMATCH,
    JILID_PROBLEM_NIM_NOT_IN_MASTER,
    JILID_PROBLEM_SCORE_OUT_OF_RANGE,
    JILID_PROBLEM_TYPE_GENDER_UNKNOWN,
    JILID_PROBLEM_TYPE_NAME_MISMATCH,
    JILID_PROBLEM_TYPE_NIM_NOT_IN_MASTER,
    JILID_PROBLEM_TYPE_ORDER,
    JILID_PROBLEM_TYPE_SCORE_OUT_OF_RANGE,
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
    name_similarity,
    natural_sort_kelas_key,
    normalize_gender,
    normalize_header,
    normalize_name_for_compare,
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


def _resolve_nim_by_name(penilaian: pd.DataFrame, master_df: pd.DataFrame) -> pd.DataFrame:
    """Koreksi NIM baris-baris yang duplikat di file nilai menggunakan nama dari master.

    Untuk setiap baris yang NIM-nya muncul lebih dari sekali, dicari padanan
    nama di file master (exact dulu, lalu similarity). Jika ketemu, NIM di baris
    tersebut diganti dengan NIM yang benar dari master agar merge selanjutnya
    bisa menemukan data mahasiswa yang tepat.
    """
    master_norm_to_nim: Dict[str, str] = {}
    master_by_first_char: Dict[str, List[Tuple[str, str]]] = defaultdict(list)

    for _, mrow in master_df.iterrows():
        nama = str(mrow.get("nama", ""))
        nim = str(mrow.get("nim", ""))
        if not nama or not nim:
            continue
        norm = normalize_name_for_compare(nama)
        if norm:
            if norm not in master_norm_to_nim:
                master_norm_to_nim[norm] = nim
            master_by_first_char[norm[0]].append((norm, nim))

    result = penilaian.copy()
    dup_mask = result["nim"].ne("") & result["nim"].duplicated(keep=False)

    for idx in result[dup_mask].index:
        nama_nilai = str(result.at[idx, "nama_nilai"] or "")
        if is_blank(nama_nilai):
            continue

        norm_nilai = normalize_name_for_compare(nama_nilai)
        if not norm_nilai:
            continue

        # Coba exact normalized match dulu (O(1))
        if norm_nilai in master_norm_to_nim:
            result.at[idx, "nim"] = master_norm_to_nim[norm_nilai]
            continue

        # Coba similarity match ke kandidat dengan huruf pertama yang sama dan panjang mirip
        best_nim: str | None = None
        best_score = 0.0
        candidates = master_by_first_char.get(norm_nilai[0], [])
        len_val = len(norm_nilai)
        matcher = SequenceMatcher(None, norm_nilai, "")
        for m_norm, m_nim in candidates:
            if abs(len(m_norm) - len_val) > 3:
                continue
            matcher.set_seq2(m_norm)
            sim = matcher.ratio()
            if sim > best_score and sim >= JILID_NAME_SIMILARITY_THRESHOLD:
                best_score = sim
                best_nim = m_nim

        if best_nim is not None:
            result.at[idx, "nim"] = best_nim

    return result


def build_jilid_recap(master_df: pd.DataFrame, penilaian_df: pd.DataFrame) -> Dict[str, Any]:
    """Gabungkan file penilaian dengan data master lalu kelompokkan per Jilid & jenis kelamin.

    Aturan klasifikasi:
    - Data diri (Nama, NIM, Prodi, Jenis Kelamin, Kelas PAI) SELALU diambil dari master.
    - NIM duplikat di file nilai: dikoreksi dengan mencari NIM yang benar dari master
      berdasarkan kesamaan nama, sebelum proses merge dilakukan.
    - Nilai kosong: langsung masuk Jilid 1 (bukan masalah).
    - Nilai di luar rentang: tetap diklasifikasikan menggunakan compute_jilid().

    Data Bermasalah hanya berisi ketidaksesuaian antara file nilai dan file master:
    1. NIM di file nilai tidak ditemukan di file master.
    2. Nama di file nilai berbeda jauh dengan nama di file master (NIM sama).
    3. Jenis Kelamin di file master kosong / tidak dikenali (L/P).
    """
    penilaian = penilaian_df.copy()
    penilaian["total_score"] = penilaian["total_nilai"].apply(parse_score)

    # Koreksi NIM duplikat menggunakan nama dari master sebelum merge
    penilaian = _resolve_nim_by_name(penilaian, master_df)

    # Setelah koreksi, deduplikat berdasarkan NIM (ambil baris terakhir)
    penilaian_unique = penilaian.drop_duplicates(subset=["nim"], keep="last")

    merged = penilaian_unique.merge(master_df, on="nim", how="left", suffixes=("_nilai", ""))

    problems: List[Dict[str, Any]] = []
    classified_rows: List[Dict[str, Any]] = []
    otomatis_rows: List[Dict[str, Any]] = []

    for _, row in merged.iterrows():
        master_found = not is_blank(row.get("kode_kelas_pai", ""))
        nama_nilai = row.get("nama_nilai", "")

        # --- Cek ketidaksesuaian nilai vs master ---
        problem_type = ""
        reason = ""

        if not master_found:
            problem_type = JILID_PROBLEM_TYPE_NIM_NOT_IN_MASTER
            reason = JILID_PROBLEM_NIM_NOT_IN_MASTER
        elif row.get("jenis_kelamin") not in ("L", "P"):
            problem_type = JILID_PROBLEM_TYPE_GENDER_UNKNOWN
            reason = JILID_PROBLEM_GENDER_UNKNOWN
        elif (
            not is_blank(nama_nilai)
            and name_similarity(row.get("nama", ""), nama_nilai) < JILID_NAME_SIMILARITY_THRESHOLD
        ):
            problem_type = JILID_PROBLEM_TYPE_NAME_MISMATCH
            reason = JILID_PROBLEM_NAME_MISMATCH

        if problem_type:
            # Nama & Prodi dari master jika ditemukan, fallback ke file nilai
            nama_display = (
                row.get("nama") if master_found and not is_blank(row.get("nama", ""))
                else nama_nilai
            )
            prodi_display = (
                row.get("prodi") if master_found and not is_blank(row.get("prodi", ""))
                else row.get("prodi_nilai", "")
            )
            problems.append({
                "NIM": row.get("nim", ""),
                "Nama": nama_display,
                "Program Studi": prodi_display,
                "Jenis Masalah": problem_type,
                "Total Nilai": row.get("total_nilai", ""),
                "Keterangan": reason,
            })
        else:
            # Tidak bermasalah dari sisi master — cek nilai
            total_score = row.get("total_score")
            score_empty = total_score is None or (isinstance(total_score, float) and pd.isna(total_score))
            if score_empty:
                # Nilai kosong → Jilid 1 otomatis
                jilid = "Jilid 1"
                keterangan = JILID_EMPTY_SCORE_NOTE
                otomatis_rows.append({
                    "NIM": row.get("nim", ""),
                    "Nama": row.get("nama", ""),
                    "Jenis Kelamin": "Laki-laki" if row.get("jenis_kelamin") == "L" else "Perempuan",
                    "Kelas PAI": row.get("kode_kelas_pai", ""),
                    "Program Studi": row.get("prodi", ""),
                    "Keterangan": JILID_EMPTY_SCORE_NOTE,
                })
            elif not (JILID_TOTAL_RANGE["min"] <= total_score <= JILID_TOTAL_RANGE["max"]):
                # Nilai di luar rentang → Data Bermasalah (data diri dari master)
                problems.append({
                    "NIM": row.get("nim", ""),
                    "Nama": row.get("nama", ""),
                    "Program Studi": row.get("prodi", ""),
                    "Jenis Masalah": JILID_PROBLEM_TYPE_SCORE_OUT_OF_RANGE,
                    "Total Nilai": row.get("total_nilai", ""),
                    "Keterangan": JILID_PROBLEM_SCORE_OUT_OF_RANGE.format(
                        total_score=total_score,
                        minimum=JILID_TOTAL_RANGE["min"],
                        maximum=JILID_TOTAL_RANGE["max"],
                    ),
                })
                continue
            else:
                jilid = compute_jilid(total_score)
                keterangan = ""
            classified_rows.append({
                "nama": row.get("nama", ""),
                "jenis_kelamin": row.get("jenis_kelamin", ""),
                "nim": row.get("nim", ""),
                "kode_kelas_pai": row.get("kode_kelas_pai", ""),
                "prodi": row.get("prodi", ""),
                "keterangan": keterangan,
                "_jilid": jilid,
            })

    # Peserta master yang Kelas PAI-nya sudah "kesentuh" gelombang ini (ada
    # peserta sekelas yang ikut tes) tapi NIM-nya sendiri tidak muncul di file
    # penilaian dianggap tidak ikut tes gelombang ini dan otomatis Jilid 1.
    # Peserta di Kelas PAI yang sama sekali belum tersentuh file penilaian ini
    # (kemungkinan besar gelombang lain) tidak disertakan sama sekali.
    tested_nim = set(penilaian_unique["nim"])
    tested_classes = set(master_df.loc[master_df["nim"].isin(tested_nim), "kode_kelas_pai"])
    untested_mask = (
        master_df["nim"].ne("")
        & ~master_df["nim"].isin(tested_nim)
        & master_df["kode_kelas_pai"].isin(tested_classes)
    )
    for _, row in master_df.loc[untested_mask].iterrows():
        if row.get("jenis_kelamin") not in ("L", "P"):
            problems.append({
                "NIM": row.get("nim", ""),
                "Nama": row.get("nama", ""),
                "Program Studi": row.get("prodi", ""),
                "Jenis Masalah": JILID_PROBLEM_TYPE_GENDER_UNKNOWN,
                "Total Nilai": "",
                "Keterangan": JILID_PROBLEM_GENDER_UNKNOWN,
            })
            continue
        classified_rows.append({
            "nama": row.get("nama", ""),
            "jenis_kelamin": row.get("jenis_kelamin", ""),
            "nim": row.get("nim", ""),
            "kode_kelas_pai": row.get("kode_kelas_pai", ""),
            "prodi": row.get("prodi", ""),
            "keterangan": JILID_AUTO_ASSIGN_NOTE,
            "_jilid": "Jilid 1",
        })
        otomatis_rows.append({
            "NIM": row.get("nim", ""),
            "Nama": row.get("nama", ""),
            "Jenis Kelamin": "Laki-laki" if row.get("jenis_kelamin") == "L" else "Perempuan",
            "Kelas PAI": row.get("kode_kelas_pai", ""),
            "Program Studi": row.get("prodi", ""),
            "Keterangan": JILID_AUTO_ASSIGN_NOTE,
        })

    valid_rows = pd.DataFrame(
        classified_rows,
        columns=["nama", "jenis_kelamin", "nim", "kode_kelas_pai", "prodi", "keterangan", "_jilid"],
    )

    data_otomatis_jilid1 = pd.DataFrame(
        otomatis_rows,
        columns=["NIM", "Nama", "Jenis Kelamin", "Kelas PAI", "Program Studi", "Keterangan"],
    )
    if not data_otomatis_jilid1.empty:
        sort_keys = data_otomatis_jilid1["Kelas PAI"].apply(natural_sort_kelas_key)
        data_otomatis_jilid1["_sort_angka"] = sort_keys.apply(lambda x: x[0])
        data_otomatis_jilid1["_sort_huruf"] = sort_keys.apply(lambda x: x[1])
        data_otomatis_jilid1["_sort_asli"] = sort_keys.apply(lambda x: x[2])
        data_otomatis_jilid1 = data_otomatis_jilid1.sort_values(
            by=["_sort_angka", "_sort_huruf", "_sort_asli", "Nama"], ascending=True
        ).drop(columns=["_sort_angka", "_sort_huruf", "_sort_asli"]).reset_index(drop=True)

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
    data_bermasalah = pd.DataFrame(
        problems,
        columns=["NIM", "Nama", "Program Studi", "Jenis Masalah", "Total Nilai", "Keterangan"],
    )

    if data_bermasalah.empty:
        masalah_ringkasan = pd.DataFrame(columns=["Jenis Masalah", "Jumlah"])
    else:
        masalah_ringkasan = data_bermasalah["Jenis Masalah"].value_counts().reset_index()
        masalah_ringkasan.columns = ["Jenis Masalah", "Jumlah"]
        masalah_ringkasan["_urutan"] = masalah_ringkasan["Jenis Masalah"].apply(
            lambda value: JILID_PROBLEM_TYPE_ORDER.index(value) if value in JILID_PROBLEM_TYPE_ORDER else 999
        )
        masalah_ringkasan = masalah_ringkasan.sort_values(
            by=["_urutan", "Jenis Masalah"], ascending=True
        ).drop(columns=["_urutan"])

    summary = {
        "total_dinilai": int(len(penilaian)),
        "total_otomatis_jilid1": int(len(data_otomatis_jilid1)),
        "total_terklasifikasi": int(len(valid_rows)),
        "total_bermasalah": int(len(data_bermasalah)),
    }

    return {
        "groups": groups,
        "ringkasan": ringkasan,
        "data_bermasalah": data_bermasalah,
        "masalah_ringkasan": masalah_ringkasan,
        "data_otomatis_jilid1": data_otomatis_jilid1,
        "summary": summary,
    }


def export_jilid_excel(
    groups: Dict[Tuple[str, str], pd.DataFrame],
    data_bermasalah: pd.DataFrame,
    masalah_ringkasan: pd.DataFrame | None = None,
    data_otomatis_jilid1: pd.DataFrame | None = None,
) -> bytes:
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
        if data_otomatis_jilid1 is not None and not data_otomatis_jilid1.empty:
            data_otomatis_jilid1.to_excel(writer, sheet_name="Otomatis Jilid 1", index=False)
        if masalah_ringkasan is not None:
            masalah_ringkasan.to_excel(writer, sheet_name="Ringkasan Masalah", index=False)
        data_bermasalah.to_excel(writer, sheet_name="Data Bermasalah", index=False)
    return output.getvalue()
