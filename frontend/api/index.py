import sys
from pathlib import Path

# Memasukkan folder frontend ke sys.path agar paket backend di frontend/backend dapat di-import oleh Vercel
frontend_dir = Path(__file__).resolve().parent.parent
if str(frontend_dir) not in sys.path:
    sys.path.insert(0, str(frontend_dir))

from backend.app.main import app
