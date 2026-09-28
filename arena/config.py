from __future__ import annotations
import hashlib
import json
import os
import tempfile
import time
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)
DATA = Path(os.environ.get("ARENA_DATA_DIR", ROOT / ".arena")).resolve()
RUNS = DATA / "runs"
MODELS = DATA / "models"
SOURCES = DATA / "sources"
DATASETS = DATA / "datasets"
for directory in (DATA, RUNS, MODELS, SOURCES, DATASETS):
    directory.mkdir(parents=True, exist_ok=True)

def digest(value) -> str:
    raw = value if isinstance(value, bytes) else json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Windows scanners may briefly hold the destination. Use a private temporary
    # name and bounded replacement retries; leave the old complete file intact.
    fd, name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(value, indent=2, ensure_ascii=False))
            stream.flush()
            os.fsync(stream.fileno())
        for attempt in range(8):
            try:
                os.replace(temp, path)
                break
            except PermissionError:
                if attempt == 7:
                    raise
                time.sleep(.05 * (attempt + 1))
    finally:
        temp.unlink(missing_ok=True)
