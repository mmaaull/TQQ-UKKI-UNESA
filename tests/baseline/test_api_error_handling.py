"""Smoke test error contract FastAPI tanpa mengubah business logic."""

from __future__ import annotations

import sys
from io import BytesIO

import pandas as pd
from fastapi.testclient import TestClient

from _app_logic import PROJECT_ROOT
from generate_baseline import NILAI_FILE, PESERTA_FILE, ensure_input_fixtures

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.main import app


def excel_bytes(columns: list[str]) -> BytesIO:
    output = BytesIO()
    pd.DataFrame(columns=columns).to_excel(output, index=False)
    output.seek(0)
    return output


def report(label: str, response, expected_status: int) -> bool:
    if response.status_code == expected_status:
        print(f"[PASS] {label}: {expected_status}")
        return True
    print(f"[FAIL] {label}: expected {expected_status}, actual {response.status_code}: {response.text}")
    return False


def main() -> int:
    ensure_input_fixtures()
    passed = True
    with TestClient(app) as client:
        passed &= report(
            "Hanya file peserta diunggah",
            client.post("/api/rekap/process", files={"peserta_file": (PESERTA_FILE.name, PESERTA_FILE.read_bytes())}),
            422,
        )
        passed &= report(
            "Format peserta tidak didukung",
            client.post(
                "/api/rekap/process",
                files={
                    "peserta_file": ("peserta.csv", b"Nama,NIM"),
                    "nilai_file": (NILAI_FILE.name, NILAI_FILE.read_bytes()),
                },
            ),
            415,
        )
        passed &= report(
            "File peserta kosong",
            client.post(
                "/api/rekap/process",
                files={
                    "peserta_file": (PESERTA_FILE.name, b""),
                    "nilai_file": (NILAI_FILE.name, NILAI_FILE.read_bytes()),
                },
            ),
            400,
        )
        passed &= report(
            "Kolom peserta tidak lengkap",
            client.post(
                "/api/rekap/process",
                files={
                    "peserta_file": ("peserta_tidak_lengkap.xlsx", excel_bytes(["Nama", "NIM"])),
                    "nilai_file": (NILAI_FILE.name, NILAI_FILE.read_bytes()),
                },
            ),
            422,
        )
        passed &= report("Session rekap tidak ditemukan", client.get("/api/rekap/tidak-ada"), 404)
        passed &= report("Session export tidak ditemukan", client.get("/api/export/tidak-ada/final"), 404)
        passed &= report(
            "Format rapikan tidak didukung",
            client.post("/api/rapikan/process", files={"rekap_file": ("rekap.csv", b"NIM")}),
            415,
        )
        passed &= report(
            "File rapikan kosong",
            client.post("/api/rapikan/process", files={"rekap_file": ("rekap.xlsx", b"")}),
            400,
        )
        passed &= report("Session rapikan tidak ditemukan", client.get("/api/rapikan/tidak-ada/download"), 404)

    print("\nAPI error handling PASSED." if passed else "\nAPI error handling FAILED.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
