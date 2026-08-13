"""Penyimpanan sesi rekap sementara untuk environment development."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Any, Dict, Optional
from uuid import uuid4

import pandas as pd


@dataclass
class RekapSession:
    """Hasil rekap yang diperlukan untuk response dan endpoint export berikutnya."""

    summary: Dict[str, Any]
    results: Dict[str, pd.DataFrame]


_sessions: Dict[str, RekapSession] = {}
_sessions_lock = RLock()


def create_rekap_session(
    summary: Dict[str, Any],
    results: Dict[str, pd.DataFrame],
) -> str:
    """Simpan hasil rekap di memori dan return UUID sesi baru."""
    session_id = str(uuid4())
    with _sessions_lock:
        _sessions[session_id] = RekapSession(summary=summary, results=results)
    return session_id


def get_rekap_session(session_id: str) -> Optional[RekapSession]:
    """Ambil sesi rekap dari memori, atau None bila tidak ditemukan."""
    with _sessions_lock:
        return _sessions.get(session_id)
