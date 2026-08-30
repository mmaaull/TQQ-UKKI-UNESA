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


@dataclass
class RapikanSession:
    """Hasil mode rapikan sementara untuk preview dan unduhan."""

    preview: pd.DataFrame
    sheet_preview: pd.DataFrame
    excel_bytes: bytes


_sessions: Dict[str, RekapSession] = {}
_rapikan_sessions: Dict[str, RapikanSession] = {}
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


def create_rapikan_session(
    preview: pd.DataFrame,
    sheet_preview: pd.DataFrame,
    excel_bytes: bytes,
) -> str:
    """Simpan hasil rapikan di memori dan return UUID sesi baru."""
    session_id = str(uuid4())
    with _sessions_lock:
        _rapikan_sessions[session_id] = RapikanSession(
            preview=preview,
            sheet_preview=sheet_preview,
            excel_bytes=excel_bytes,
        )
    return session_id


def get_rapikan_session(session_id: str) -> Optional[RapikanSession]:
    """Ambil sesi rapikan dari memori, atau None bila tidak ditemukan."""
    with _sessions_lock:
        return _rapikan_sessions.get(session_id)
