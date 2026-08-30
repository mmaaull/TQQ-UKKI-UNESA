"""Verifikasi wrapper FastAPI terhadap baseline Streamlit tanpa mengubah fixture."""

from __future__ import annotations

import json
import sys
from io import BytesIO

import pandas as pd
from fastapi.testclient import TestClient

from _app_logic import PROJECT_ROOT
from generate_baseline import EXPECTED_DIR, NILAI_FILE, PESERTA_FILE, ensure_input_fixtures
from verify_baseline import compare_dataframe, compare_excel, report

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app
from backend.app.services.rapikan_service import (
    build_rekap_kelas_prodi_preview,
    drop_rekap_internal_columns,
    export_rekap_by_kelas_prodi,
    read_rekap_file,
)


API_DATA_BASELINES = {
    "Hasil merge / status nilai / status validasi": ("hasil_rekap.csv", "rekap"),
    "Data bermasalah": ("data_bermasalah.csv", "data_bermasalah"),
    "Ringkasan kelas": ("ringkasan_kelas.csv", "ringkasan_kelas"),
    "Ringkasan masalah": ("ringkasan_masalah.csv", "ringkasan_masalah"),
}

API_EXPORT_BASELINES = {
    "Export final": ("final", "export_final.xlsx"),
    "Export validasi": ("validasi", "export_validasi.xlsx"),
    "Export data bermasalah": ("data-bermasalah", "export_data_bermasalah.xlsx"),
}


def compare_excel_bytes(expected_bytes: bytes, actual_bytes: bytes) -> list[str]:
    with pd.ExcelFile(BytesIO(expected_bytes)) as expected_book, pd.ExcelFile(BytesIO(actual_bytes)) as actual_book:
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


def main() -> int:
    ensure_input_fixtures()
    passed = True

    with TestClient(app) as client, PESERTA_FILE.open("rb") as peserta, NILAI_FILE.open("rb") as nilai:
        response = client.post(
            "/api/rekap/process",
            files={
                "peserta_file": (PESERTA_FILE.name, peserta, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                "nilai_file": (NILAI_FILE.name, nilai, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            },
        )
        passed &= report("FastAPI proses rekap tersedia", [] if response.status_code == 200 else [response.text])
        if response.status_code != 200:
            return 1
        payload = response.json()

        expected_summary = json.loads((EXPECTED_DIR / "summary.json").read_text(encoding="utf-8"))
        passed &= report(
            "Summary FastAPI",
            [] if payload["summary"] == expected_summary else [f"Expected: {expected_summary}", f"Actual: {payload['summary']}"],
        )

        for label, (filename, response_key) in API_DATA_BASELINES.items():
            expected = pd.read_csv(EXPECTED_DIR / filename, dtype=str, keep_default_na=False)
            actual = pd.DataFrame(payload[response_key])
            passed &= report(label, compare_dataframe(expected, actual))

        session_response = client.get(f"/api/rekap/{payload['session_id']}")
        passed &= report(
            "Session FastAPI",
            [] if session_response.status_code == 200 and session_response.json()["summary"] == expected_summary else [session_response.text],
        )

        for label, (endpoint, filename) in API_EXPORT_BASELINES.items():
            export_response = client.get(f"/api/export/{payload['session_id']}/{endpoint}")
            differences = [] if export_response.status_code == 200 else [export_response.text]
            if not differences:
                differences = compare_excel(EXPECTED_DIR / filename, export_response.content)
            passed &= report(f"FastAPI {label}", differences)

        per_kelas = client.get(f"/api/export/{payload['session_id']}/per-kelas")
        passed &= report(
            "FastAPI export per kelas",
            [] if per_kelas.status_code == 200 and per_kelas.headers.get("content-type") == "application/zip" and per_kelas.content else [per_kelas.text],
        )
        template = client.get("/api/export/template")
        passed &= report(
            "FastAPI export template",
            [] if template.status_code == 200 and template.content else [template.text],
        )

    rapikan_input = EXPECTED_DIR / "export_final.xlsx"
    with rapikan_input.open("rb") as source_file:
        legacy_rapikan = read_rekap_file(source_file)
    expected_preview = drop_rekap_internal_columns(legacy_rapikan).head(100)
    expected_sheet_preview = build_rekap_kelas_prodi_preview(legacy_rapikan)
    expected_rapikan_export = export_rekap_by_kelas_prodi(legacy_rapikan)

    with TestClient(app) as client, rapikan_input.open("rb") as source_file:
        rapikan_response = client.post(
            "/api/rapikan/process",
            files={"rekap_file": (rapikan_input.name, source_file, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        passed &= report("FastAPI mode rapikan tersedia", [] if rapikan_response.status_code == 200 else [rapikan_response.text])
        if rapikan_response.status_code == 200:
            rapikan_payload = rapikan_response.json()
            passed &= report("Preview rapikan", compare_dataframe(expected_preview, pd.DataFrame(rapikan_payload["preview"])))
            passed &= report("Preview sheet rapikan", compare_dataframe(expected_sheet_preview, pd.DataFrame(rapikan_payload["sheet_preview"])))
            rapikan_download = client.get(f"/api/rapikan/{rapikan_payload['session_id']}/download")
            differences = [] if rapikan_download.status_code == 200 else [rapikan_download.text]
            if not differences:
                differences = compare_excel_bytes(expected_rapikan_export, rapikan_download.content)
            passed &= report("Export mode rapikan", differences)

    print()
    print("FastAPI integration verification PASSED." if passed else "FastAPI integration verification FAILED.")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
