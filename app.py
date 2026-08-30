"""Compatibility module for legacy baseline tools.

The application entry points are now FastAPI (``backend.app.main``) and
Next.js (``frontend``).  This module deliberately contains no UI code; it
re-exports the established business services so existing baseline scripts can
continue to validate their output without the retired UI runtime.
"""

from backend.app.core.config import *  # noqa: F403
from backend.app.services.excel_service import *  # noqa: F403
from backend.app.services.processing import *  # noqa: F403
from backend.app.services.rapikan_service import *  # noqa: F403
from backend.app.utils.helpers import *  # noqa: F403
