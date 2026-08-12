"""Memuat fungsi business logic dari app.py tanpa mengeksekusi UI Streamlit."""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_PATH = PROJECT_ROOT / "app.py"
UI_MARKER = "# STREAMLIT UI - WEB DASHBOARD STYLE"


def load_app_logic() -> ModuleType:
    """Return modul logic aplikasi yang sama persis, tanpa entry point UI.

    `app.py` saat ini mengeksekusi dashboard di level modul. Baseline hanya
    mengompilasi bagian sebelum penanda UI agar fungsi produksi seperti
    `standardize_dataframe`, `process_rekap`, dan fungsi export dapat dipakai
    tanpa `streamlit run` atau browser.
    """
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    source = APP_PATH.read_text(encoding="utf-8")
    if UI_MARKER not in source:
        raise RuntimeError(f"Penanda UI tidak ditemukan di {APP_PATH}")

    logic_source = source.split(UI_MARKER, 1)[0]
    module = ModuleType("tqq_streamlit_business_logic")
    module.__file__ = str(APP_PATH)
    exec(compile(logic_source, str(APP_PATH), "exec"), module.__dict__)
    return module
