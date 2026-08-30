import sys
from pathlib import Path
# Hubungkan folder root project agar modul backend dapat di-import
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))
from backend.app.main import app