# worker.py
import os
import threading
import json
import tempfile
import shutil
import traceback
from pathlib import Path

from .analyzer import build_report
from .utils import safe_extract_archive
from .storage import get_job, set_job   # include both if used


REDIS_URL = os.getenv("REDIS_URL", None)

if REDIS_URL:
    # RQ mode: enqueue a callable
    from rq import Queue
    import redis
    redis_conn = redis.from_url(REDIS_URL)
    q = Queue(connection=redis_conn)
    def enqueue_job(archive_path: str, job_id: str):
        q.enqueue('worker._run_job', archive_path, job_id)  # Note: when using RQ, module path must be importable
else:
    def enqueue_job(archive_path: str, job_id: str):
        t = threading.Thread(target=_run_job, args=(archive_path, job_id), daemon=True)
        t.start()

def _run_job(archive_path: str, job_id: str):
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    tmpdir = tempfile.mkdtemp(prefix="ext_")
    try:
        extracted = safe_extract_archive(archive_path, tmpdir)
        report = build_report(extracted, job_id)
        report_path = reports_dir / f"{job_id}.json"
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        meta = {"job_id": job_id, "status": "finished", "report_path": str(report_path)}
        set_job(job_id, meta)
    except Exception as e:
        err = traceback.format_exc()
        meta = {"job_id": job_id, "status": "error", "error": str(e), "traceback": err}
        set_job(job_id, meta)
    finally:
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass
