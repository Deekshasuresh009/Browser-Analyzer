# storage.py
import json
from pathlib import Path
from threading import Lock

DB_PATH = Path("jobs_db.json")
_lock = Lock()

def _read_db():
    if not DB_PATH.exists():
        return {}
    try:
        return json.loads(DB_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def _write_db(d):
    DB_PATH.write_text(json.dumps(d, indent=2), encoding="utf-8")

def set_job(job_id: str, data: dict):
    with _lock:
        d = _read_db()
        d[job_id] = data
        _write_db(d)

def get_job(job_id: str):
    d = _read_db()
    return d.get(job_id)
