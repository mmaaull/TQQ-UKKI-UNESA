"""Entry point FastAPI dasar untuk backend TQQ."""

import json
from io import BytesIO
from pathlib import Path
from typing import Callable

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from backend.app.core.config import NILAI_COLUMN_ALIASES, PESERTA_COLUMN_ALIASES
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
    create_rekap_session,
    get_rekap_session,
)


app = FastAPI(title="Rekap Nilai TQQ Akbar UNESA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    """Memastikan service FastAPI tersedia."""
    return {"status": "ok"}


def dataframe_records(df: pd.DataFrame) -> list[dict]:
    """Mengubah DataFrame hasil service menjadi data JSON untuk response API."""
    return json.loads(df.to_json(orient="records"))


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


async def read_excel_upload(upload: UploadFile, field_name: str) -> pd.DataFrame:
    """Validasi upload API lalu gunakan pembaca file legacy yang sama."""
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
        return read_uploaded_file(uploaded_file)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} tidak dapat dibaca sebagai file Excel: {exc}",
        ) from exc


@app.post("/api/rekap/process")
async def process_rekap_upload(
    peserta_file: UploadFile = File(...),
    nilai_file: UploadFile = File(...),
) -> dict:
    """Menjalankan business logic rekap legacy terhadap dua file Excel."""
    raw_peserta = await read_excel_upload(peserta_file, "peserta_file")
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
