"""Start Nginx Log Dashboard with bundled offline dependencies."""

import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
PYLIB_DIR = BASE_DIR / "pylib_py37"
DEFAULT_LOG = BASE_DIR / "sample_access.log"

sys.path.insert(0, str(BASE_DIR))
if PYLIB_DIR.is_dir():
    sys.path.insert(0, str(PYLIB_DIR))

os.environ.setdefault("LOG_FILE_PATH", str(DEFAULT_LOG))

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
        reload=False,
    )
