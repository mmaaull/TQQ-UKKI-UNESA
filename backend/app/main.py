"""Entry point FastAPI dasar untuk backend TQQ."""

import asyncio
from io import BytesIO
from pathlib import Path
from typing import Callable

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from backend.app.core.config import CORS_ORIGINS, NILAI_COLUMN_ALIASES, PESERTA_COLUMN_ALIASES
from backend.app.services.processing import (
    process_rekap,
    read_uploaded_file,
    standardize_dataframe,
)
from backend.app.services.excel_service import (
    create_template_excel,
    export_data_bermasalah_excel,
    export_excel,
    export_laporan_validasi_excel,
    export_per_kelas_zip,
)
from backend.app.services.session_store import (
    create_jilid_session,
    create_rapikan_session,
    create_rekap_session,
    create_tentor_session,
    get_jilid_session,
    get_rapikan_session,
    get_rekap_session,
    get_tentor_session,
)
from backend.app.services.rapikan_service import (
    RekapRequiredColumnError,
    build_rekap_kelas_prodi_preview,
    drop_rekap_internal_columns,
    export_rekap_by_kelas_prodi,
    read_rekap_file,
)
from backend.app.services.jilid_service import (
    MasterRequiredColumnError,
    PenilaianRequiredColumnError,
    build_jilid_recap,
    export_jilid_excel,
    read_master_file,
    read_penilaian_tashih_file,
)
from backend.app.services.tentor_service import (
    TentorAllocationError,
    TentorRequiredDataError,
    build_tentor_distribution,
    export_tentor_excel,
    read_jilid_recap_file,
)
from backend.app.utils.helpers import read_all_sheets


app = FastAPI(title="Rekap Nilai TQQ Akbar UNESA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Memastikan service FastAPI tersedia."""
    return {"status": "ok"}


def dataframe_records(df: pd.DataFrame) -> list[dict]:
    """Mengubah DataFrame hasil service menjadi data JSON untuk response API."""
    # ``DataFrame.to_json`` membatasi presisi float secara default. Gunakan
    # record Python agar nilai hasil validasi (mis. kemiripan nama) tidak
    # berubah ketika diserialisasi ke response API.
    normalized = df.astype(object).where(pd.notna(df), None)
    return normalized.to_dict(orient="records")


def build_summary(results: dict[str, pd.DataFrame]) -> dict[str, int | float]:
    """Bentuk summary API dari hasil business logic legacy."""
    total_peserta = len(results["rekap"])
    sudah_ada_nilai = len(results["sudah_ada_nilai"])
    return {
        "total_peserta": total_peserta,
        "sudah_ada_nilai": sudah_ada_nilai,
        "belum_ada_nilai": len(results["belum_ada_nilai"]),
        "perlu_dicek": len(results["perlu_dicek"]),
        "persentase_selesai": (
            sudah_ada_nilai / total_peserta * 100 if total_peserta else 0
        ),
    }


def rekap_response(
    session_id: str,
    summary: dict[str, int | float],
    results: dict[str, pd.DataFrame],
) -> dict:
    """Serialisasi hasil sesi tanpa mengubah DataFrame dari service legacy."""
    return {
        "session_id": session_id,
        "summary": summary,
        "rekap": dataframe_records(results["rekap"]),
        "ringkasan_kelas": dataframe_records(results["ringkasan"]),
        "ringkasan_masalah": dataframe_records(results["masalah_ringkasan"]),
        "data_bermasalah": dataframe_records(results["data_bermasalah"]),
    }


async def read_excel_upload(
    upload: UploadFile,
    field_name: str,
    reader: Callable[[BytesIO], pd.DataFrame] = read_uploaded_file,
) -> pd.DataFrame:
    """Validasi upload API lalu baca file menggunakan reader yang diberikan."""
    filename = upload.filename or ""
    if Path(filename).suffix.lower() not in {".xlsx", ".xls"}:
        raise HTTPException(
            status_code=415,
            detail=f"{field_name} harus berformat .xlsx atau .xls.",
        )

    contents = await upload.read()
    if not contents:
        raise HTTPException(status_code=400, detail=f"{field_name} kosong.")

    uploaded_file = BytesIO(contents)
    uploaded_file.name = filename
    try:
        return reader(uploaded_file)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} tidak dapat dibaca sebagai file Excel: {exc}",
        ) from exc


async def read_rapikan_upload(upload: UploadFile) -> pd.DataFrame:
    """Baca file hasil rekap melalui service legacy mode rapikan."""
    filename = upload.filename or ""
    if Path(filename).suffix.lower() not in {".xlsx", ".xls"}:
        raise HTTPException(
            status_code=415,
            detail="rekap_file harus berformat .xlsx atau .xls.",
        )
    contents = await upload.read()
    if not contents:
        raise HTTPException(status_code=400, detail="rekap_file kosong.")
    uploaded_file = BytesIO(contents)
    uploaded_file.name = filename
    try:
        dataframe = read_rekap_file(uploaded_file)
    except RekapRequiredColumnError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"rekap_file tidak dapat dibaca sebagai file Excel: {exc}",
        ) from exc
    if dataframe.empty:
        raise HTTPException(status_code=422, detail="Data rekap kosong atau tidak ditemukan.")
    return dataframe


@app.post("/api/rekap/process")
async def process_rekap_upload(
    peserta_file: UploadFile = File(...),
    nilai_file: UploadFile = File(...),
) -> dict:
    """Menjalankan business logic rekap legacy terhadap dua file Excel."""
    raw_peserta = await read_excel_upload(peserta_file, "peserta_file", reader=read_all_sheets)
    raw_nilai = await read_excel_upload(nilai_file, "nilai_file")

    peserta_df, missing_peserta = standardize_dataframe(
        raw_peserta,
        PESERTA_COLUMN_ALIASES,
        "peserta",
    )
    nilai_df, missing_nilai = standardize_dataframe(
        raw_nilai,
        NILAI_COLUMN_ALIASES,
        "nilai",
    )
    if missing_peserta or missing_nilai:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Ada kolom wajib yang belum ditemukan.",
                "peserta": missing_peserta,
                "nilai": missing_nilai,
            },
        )

    try:
        results = process_rekap(peserta_df, nilai_df)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Proses rekap gagal.") from exc

    summary = build_summary(results)
    session_id = create_rekap_session(summary, results)
    return rekap_response(session_id, summary, results)


@app.get("/api/rekap/{session_id}")
def get_rekap_result(session_id: str) -> dict:
    """Mengambil hasil rekap yang tersimpan dalam sesi development."""
    session = get_rekap_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session rekap tidak ditemukan.")
    return rekap_response(session_id, session.summary, session.results)


@app.post("/api/rapikan/process")
async def process_rapikan_upload(rekap_file: UploadFile = File(...)) -> dict:
    """Jalankan mode rapikan legacy dan simpan hasilnya sementara."""
    combined_rekap = await read_rapikan_upload(rekap_file)
    try:
        sheet_preview = build_rekap_kelas_prodi_preview(combined_rekap)
        excel_bytes = export_rekap_by_kelas_prodi(combined_rekap)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Proses rapikan gagal.") from exc

    preview = drop_rekap_internal_columns(combined_rekap).head(100)
    session_id = create_rapikan_session(preview, sheet_preview, excel_bytes)
    return {
        "session_id": session_id,
        "summary": {
            "total_data": int(len(combined_rekap)),
            "total_sheet": int(len(sheet_preview)),
        },
        "preview": dataframe_records(preview),
        "sheet_preview": dataframe_records(sheet_preview),
    }


@app.get("/api/rapikan/{session_id}/download")
def download_rapikan_result(session_id: str) -> Response:
    """Download Excel hasil mode rapikan dari sesi development."""
    session = get_rapikan_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session rapikan tidak ditemukan.")
    return Response(
        content=session.excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="rekap_tqq_per_kode_kelas_dan_prodi.xlsx"'
        },
    )


async def read_master_upload(upload: UploadFile) -> pd.DataFrame:
    """Baca file master (data keseluruhan peserta) untuk mode rekap jilid."""
    filename = upload.filename or ""
    if Path(filename).suffix.lower() not in {".xlsx", ".xls"}:
        raise HTTPException(status_code=415, detail="master_file harus berformat .xlsx atau .xls.")
    contents = await upload.read()
    if not contents:
        raise HTTPException(status_code=400, detail="master_file kosong.")
    uploaded_file = BytesIO(contents)
    uploaded_file.name = filename
    try:
        dataframe = await asyncio.to_thread(read_master_file, uploaded_file)
    except MasterRequiredColumnError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"master_file tidak dapat dibaca sebagai file Excel: {exc}",
        ) from exc
    if dataframe.empty:
        raise HTTPException(status_code=422, detail="Data master kosong atau tidak ditemukan.")
    return dataframe


async def read_penilaian_tashih_upload(upload: UploadFile) -> pd.DataFrame:
    """Baca file penilaian tashih untuk mode rekap jilid."""
    filename = upload.filename or ""
    if Path(filename).suffix.lower() not in {".xlsx", ".xls"}:
        raise HTTPException(status_code=415, detail="penilaian_file harus berformat .xlsx atau .xls.")
    contents = await upload.read()
    if not contents:
        raise HTTPException(status_code=400, detail="penilaian_file kosong.")
    uploaded_file = BytesIO(contents)
    uploaded_file.name = filename
    try:
        dataframe = await asyncio.to_thread(read_penilaian_tashih_file, uploaded_file)
    except PenilaianRequiredColumnError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"penilaian_file tidak dapat dibaca sebagai file Excel: {exc}",
        ) from exc
    if dataframe.empty:
        raise HTTPException(status_code=422, detail="Data penilaian kosong atau tidak ditemukan.")
    return dataframe


@app.post("/api/rekap-jilid/process")
async def process_rekap_jilid_upload(
    master_file: UploadFile = File(...),
    penilaian_file: UploadFile = File(...),
) -> dict:
    """Rekap pembagian kelas jilid berdasarkan file master dan file penilaian tashih."""
    master_df = await read_master_upload(master_file)
    penilaian_df = await read_penilaian_tashih_upload(penilaian_file)

    try:
        recap = await asyncio.to_thread(build_jilid_recap, master_df, penilaian_df)
        excel_bytes = await asyncio.to_thread(
            export_jilid_excel,
            recap["groups"],
            recap["data_bermasalah"],
            recap["masalah_ringkasan"],
            recap["data_otomatis_jilid1"],
        )
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Proses rekap jilid gagal: {exc}") from exc

    session_id = create_jilid_session(excel_bytes)
    return {
        "session_id": session_id,
        "summary": recap["summary"],
        "ringkasan_jilid": dataframe_records(recap["ringkasan"]),
        "ringkasan_masalah": dataframe_records(recap["masalah_ringkasan"]),
        "data_bermasalah": dataframe_records(recap["data_bermasalah"]),
        "data_otomatis_jilid1": dataframe_records(recap["data_otomatis_jilid1"]),
    }


@app.get("/api/rekap-jilid/{session_id}/download")
def download_rekap_jilid(session_id: str) -> Response:
    """Download Excel hasil rekap pembagian kelas jilid dari sesi development."""
    session = get_jilid_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session rekap jilid tidak ditemukan.")
    return Response(
        content=session.excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="rekap_pembagian_kelas_jilid.xlsx"'
        },
    )


def _validate_jumlah_tentor(jumlah_tentor_laki_laki: int, jumlah_tentor_perempuan: int) -> None:
    if jumlah_tentor_laki_laki < 0 or jumlah_tentor_perempuan < 0:
        raise HTTPException(status_code=422, detail="Jumlah tentor tidak boleh negatif.")


def _process_tentor_from_bytes(
    excel_bytes: bytes,
    filename: str,
    jumlah_tentor_laki_laki: int,
    jumlah_tentor_perempuan: int,
) -> dict:
    """Jalankan pembagian tentor dari bytes file hasil Rekap Jilid dan simpan sesinya."""
    uploaded_file = BytesIO(excel_bytes)
    uploaded_file.name = filename

    try:
        jilid_groups = read_jilid_recap_file(uploaded_file)
    except TentorRequiredDataError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"File hasil Rekap Jilid tidak dapat dibaca sebagai file Excel: {exc}",
        ) from exc

    try:
        distribution = build_tentor_distribution(
            jilid_groups, jumlah_tentor_laki_laki, jumlah_tentor_perempuan
        )
    except (TentorRequiredDataError, TentorAllocationError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    result_excel_bytes = export_tentor_excel(distribution["tentor_sheets"], distribution["ringkasan"])
    session_id = create_tentor_session(result_excel_bytes)
    return {
        "session_id": session_id,
        "summary": distribution["summary"],
        "ringkasan_tentor": dataframe_records(distribution["ringkasan"]),
    }


@app.post("/api/tentor/process")
async def process_tentor_upload(
    rekap_jilid_file: UploadFile = File(...),
    jumlah_tentor_laki_laki: int = Form(...),
    jumlah_tentor_perempuan: int = Form(...),
) -> dict:
    """Bagi peserta hasil Rekap Jilid ke tentor dari file yang diupload manual."""
    _validate_jumlah_tentor(jumlah_tentor_laki_laki, jumlah_tentor_perempuan)

    filename = rekap_jilid_file.filename or ""
    if Path(filename).suffix.lower() not in {".xlsx", ".xls"}:
        raise HTTPException(
            status_code=415,
            detail="rekap_jilid_file harus berformat .xlsx atau .xls.",
        )
    contents = await rekap_jilid_file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="rekap_jilid_file kosong.")

    return _process_tentor_from_bytes(
        contents, filename, jumlah_tentor_laki_laki, jumlah_tentor_perempuan
    )


@app.post("/api/tentor/process-from-jilid/{session_id}")
async def process_tentor_from_jilid_session(
    session_id: str,
    jumlah_tentor_laki_laki: int = Form(...),
    jumlah_tentor_perempuan: int = Form(...),
) -> dict:
    """Bagi peserta ke tentor langsung dari session Rekap Jilid yang baru diproses,
    tanpa perlu download lalu upload ulang filenya."""
    _validate_jumlah_tentor(jumlah_tentor_laki_laki, jumlah_tentor_perempuan)

    jilid_session = get_jilid_session(session_id)
    if jilid_session is None:
        raise HTTPException(status_code=404, detail="Session rekap jilid tidak ditemukan.")

    return _process_tentor_from_bytes(
        jilid_session.excel_bytes,
        "rekap_pembagian_kelas_jilid.xlsx",
        jumlah_tentor_laki_laki,
        jumlah_tentor_perempuan,
    )


@app.get("/api/tentor/{session_id}/download")
def download_tentor_result(session_id: str) -> Response:
    """Download Excel hasil pembagian tentor dari sesi development."""
    session = get_tentor_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session pembagian tentor tidak ditemukan.")
    return Response(
        content=session.excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="pembagian_tentor_tqq_akbar.xlsx"'
        },
    )


EXCEL_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def get_session_results(session_id: str) -> dict[str, pd.DataFrame]:
    """Ambil data hasil rekap session untuk digunakan oleh export legacy."""
    session = get_rekap_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session rekap tidak ditemukan.")
    return session.results


def export_download(
    export_function: Callable[[dict[str, pd.DataFrame]], bytes],
    results: dict[str, pd.DataFrame],
    filename: str,
    media_type: str,
) -> Response:
    """Jalankan fungsi export legacy dan return sebagai file download API."""
    try:
        content = export_function(results)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Export {filename} gagal: {exc}",
        ) from exc
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/export/{session_id}/final")
def export_final(session_id: str) -> Response:
    """Download Excel final per Kode Kelas PAI dari session rekap."""
    return export_download(
        export_excel,
        get_session_results(session_id),
        "hasil_rekap_tqq_akbar_per_kode_kelas_pai.xlsx",
        EXCEL_MEDIA_TYPE,
    )


@app.get("/api/export/{session_id}/validasi")
def export_validasi(session_id: str) -> Response:
    """Download laporan validasi dari session rekap."""
    return export_download(
        export_laporan_validasi_excel,
        get_session_results(session_id),
        "laporan_validasi_rekap_tqq.xlsx",
        EXCEL_MEDIA_TYPE,
    )


@app.get("/api/export/{session_id}/data-bermasalah")
def export_data_bermasalah(session_id: str) -> Response:
    """Download laporan data bermasalah dari session rekap."""
    return export_download(
        export_data_bermasalah_excel,
        get_session_results(session_id),
        "data_bermasalah_rekap_tqq.xlsx",
        EXCEL_MEDIA_TYPE,
    )


@app.get("/api/export/{session_id}/per-kelas")
def export_per_kelas(session_id: str) -> Response:
    """Download ZIP rekap terpisah per kelas dari session rekap."""
    return export_download(
        export_per_kelas_zip,
        get_session_results(session_id),
        "rekap_per_kelas_tqq_akbar.zip",
        "application/zip",
    )


@app.get("/api/export/template")
def export_template() -> Response:
    """Download template Excel legacy tanpa membutuhkan session rekap."""
    try:
        content = create_template_excel()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Export template gagal: {exc}") from exc
    return Response(
        content=content,
        media_type=EXCEL_MEDIA_TYPE,
        headers={
            "Content-Disposition": 'attachment; filename="template_rekap_tqq_akbar.xlsx"'
        },
    )
