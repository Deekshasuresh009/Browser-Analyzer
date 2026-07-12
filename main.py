from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import uuid
import aiofiles

# correct relative import – use worker inside app package
from .worker import enqueue_job
from .storage import set_job, get_job
from .analyzer import analyze_url

UPLOAD_DIR = Path("uploads"); UPLOAD_DIR.mkdir(exist_ok=True)
REPORT_DIR = Path("reports"); REPORT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Browser Extension Privacy Analyzer - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if True else ["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_EXTS = (".zip", ".crx", ".xpi")

@app.post("/upload")
async def upload_extension(file: UploadFile = File(...)):
    if not any(file.filename.endswith(ext) for ext in ALLOWED_EXTS):
        raise HTTPException(status_code=400, detail="Unsupported file type. allowed: .zip, .crx, .xpi")
    job_id = str(uuid.uuid4())
    save_name = f"{job_id}_{file.filename}"
    save_path = UPLOAD_DIR / save_name

    # write file in streaming fashion
    try:
        async with aiofiles.open(save_path, "wb") as out_file:
            while True:
                chunk = await file.read(1024*1024)
                if not chunk:
                    break
                await out_file.write(chunk)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {e}")

    # create job metadata
    meta = {"job_id": job_id, "status": "queued", "filename": save_name}
    set_job(job_id, meta)

    # enqueue background work
    enqueue_job(str(save_path), job_id)

    return {"job_id": job_id, "status_url": f"/status/{job_id}", "report_url": f"/report/{job_id}"}

@app.get("/status/{job_id}")
def status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@app.get("/report/{job_id}")
def get_report(job_id: str):
    report_file = REPORT_DIR / f"{job_id}.json"
    if report_file.exists():
        return FileResponse(str(report_file), media_type="application/json", filename=f"{job_id}.json")
    job = get_job(job_id)
    if job and job.get("status") == "queued":
        return JSONResponse({"status":"queued"}, status_code=202)
    if job and job.get("status") == "error":
        return JSONResponse({"status":"error", "error": job.get("error")}, status_code=500)
    raise HTTPException(status_code=404, detail="Report not ready")

@app.get("/download/{job_id}")
def download_report(job_id: str):
    return get_report(job_id)

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/analyze-url")
async def analyze_url_endpoint(payload: dict = Body(...)):
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")
    try:
        return analyze_url(url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
