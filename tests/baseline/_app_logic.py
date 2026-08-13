"""Memuat shim business logic aplikasi tanpa menjalankan antarmuka web."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_PATH = PROJECT_ROOT / "app.py"


def load_app_logic() -> ModuleType:
    """Return modul business logic tanpa menjalankan UI atau browser."""
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))

    spec = importlib.util.spec_from_file_location("tqq_business_logic", APP_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Modul logic tidak dapat dimuat dari {APP_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
