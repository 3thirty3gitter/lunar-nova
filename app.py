from fastapi import FastAPI, UploadFile, File, HTTPException, Form, BackgroundTasks
from typing import List
from fastapi.responses import FileResponse
import shutil
import os
import uuid
from engine import get_engine
from datetime import datetime
import json

app = FastAPI(title="Local 3D AI Engine")

# Directories
TEMP_DIR = "temp_inputs"
OUTPUT_DIR = "outputs"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading engine... (this may take a moment)")
# Pre-load engine on startup
engine = get_engine()

# In-memory job tracking (for single-process use)
JOBS = {}
JOBS_FILE = os.path.join(OUTPUT_DIR, "jobs.json")
JOBS_LOCK = None
try:
    from threading import Lock
    JOBS_LOCK = Lock()
except Exception:
    JOBS_LOCK = None


def _load_jobs():
    if not os.path.exists(JOBS_FILE):
        return
    try:
        with open(JOBS_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if isinstance(data, dict):
            JOBS.update(data)
    except Exception:
        pass


def _save_jobs():
    try:
        with open(JOBS_FILE, "w", encoding="utf-8") as handle:
            json.dump(JOBS, handle, indent=2)
    except Exception:
        pass


def _set_job(job_id, **fields):
    if JOBS_LOCK:
        with JOBS_LOCK:
            JOBS.setdefault(job_id, {"job_id": job_id}).update(fields)
    else:
        JOBS.setdefault(job_id, {"job_id": job_id}).update(fields)
    _save_jobs()


def _get_job(job_id):
    if JOBS_LOCK:
        with JOBS_LOCK:
            return JOBS.get(job_id)
    return JOBS.get(job_id)


def _list_jobs(limit=25):
    jobs = list(JOBS.values())
    jobs.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return jobs[:limit]


_load_jobs()


def _run_generation_job(
    job_id,
    input_paths,
    run_output_dir,
    *,
    resolution,
    threshold,
    smoothing_iterations,
    smoothing_lambda,
    texture_bake,
):
    try:
        _set_job(job_id, status="running", message="Generating 3D mesh...")
        output_glb_path = engine.generate(
            input_paths,
            run_output_dir,
            resolution=resolution,
            threshold=threshold,
            smoothing_iterations=smoothing_iterations,
            smoothing_lambda=smoothing_lambda,
            texture_bake=texture_bake,
        )

        if not output_glb_path or not os.path.exists(output_glb_path):
            _set_job(job_id, status="error", message="Generation failed")
            return

        _set_job(job_id, status="complete", message="Generation complete", output=output_glb_path)
    except Exception as e:
        _set_job(job_id, status="error", message=str(e))
    finally:
        try:
            for input_path in input_paths:
                if os.path.exists(input_path):
                    os.remove(input_path)
        except Exception:
            pass

@app.post("/generate")
async def generate_3d(
    files: List[UploadFile] = File(...),
    resolution: int = Form(512),
    threshold: float = Form(30.0),
    smoothing: str = Form("medium"),
    texture_bake: bool = Form(False),
):
    """
    Standard endpoint: Upload image, get 3D model (GLB) back.
    """
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")

        unique_id = str(uuid.uuid4())
        input_paths = []
        for idx, upload in enumerate(files):
            file_ext = upload.filename.split(".")[-1]
            input_filename = f"{unique_id}_{idx}.{file_ext}"
            input_path = os.path.join(TEMP_DIR, input_filename)
            with open(input_path, "wb") as buffer:
                shutil.copyfileobj(upload.file, buffer)
            input_paths.append(input_path)
            
        # Generate
        # Create a unique output folder for this run
        run_output_dir = os.path.join(OUTPUT_DIR, unique_id)
        
        resolution = 512 if resolution not in (256, 512) else resolution
        threshold = float(threshold)

        smoothing_map = {
            "none": (0, 0.0),
            "low": (8, 0.1),
            "medium": (15, 0.1),
            "high": (25, 0.15),
        }
        smoothing_key = (smoothing or "medium").lower()
        smoothing_iterations, smoothing_lambda = smoothing_map.get(
            smoothing_key,
            smoothing_map["medium"],
        )

        output_glb_path = engine.generate(
            input_paths,
            run_output_dir,
            resolution=resolution,
            threshold=threshold,
            smoothing_iterations=smoothing_iterations,
            smoothing_lambda=smoothing_lambda,
            texture_bake=texture_bake,
        )
        
        if not output_glb_path or not os.path.exists(output_glb_path):
            raise HTTPException(status_code=500, detail="Generation failed to produce output")
            
        return FileResponse(
            output_glb_path, 
            media_type="model/gltf-binary", 
            filename=f"model_{unique_id}.glb"
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup input? Maybe keep for debug for now
        pass


@app.post("/generate_async")
async def generate_3d_async(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    resolution: int = Form(512),
    threshold: float = Form(30.0),
    smoothing: str = Form("medium"),
    texture_bake: bool = Form(False),
):
    """
    Async endpoint: Upload image, get a job id back.
    Use /status/{job_id} and /result/{job_id} to poll + download.
    """
    try:
        job_id = str(uuid.uuid4())
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")

        input_paths = []
        for idx, upload in enumerate(files):
            file_ext = upload.filename.split(".")[-1]
            input_filename = f"{job_id}_{idx}.{file_ext}"
            input_path = os.path.join(TEMP_DIR, input_filename)

            with open(input_path, "wb") as buffer:
                shutil.copyfileobj(upload.file, buffer)
            input_paths.append(input_path)

        run_output_dir = os.path.join(OUTPUT_DIR, job_id)

        resolution = 512 if resolution not in (256, 512) else resolution
        threshold = float(threshold)

        smoothing_map = {
            "none": (0, 0.0),
            "low": (8, 0.1),
            "medium": (15, 0.1),
            "high": (25, 0.15),
        }
        smoothing_key = (smoothing or "medium").lower()
        smoothing_iterations, smoothing_lambda = smoothing_map.get(
            smoothing_key,
            smoothing_map["medium"],
        )

        _set_job(
            job_id,
            status="queued",
            message="Queued",
            created_at=datetime.utcnow().isoformat() + "Z",
        )
        background_tasks.add_task(
            _run_generation_job,
            job_id,
            input_paths,
            run_output_dir,
            resolution=resolution,
            threshold=threshold,
            smoothing_iterations=smoothing_iterations,
            smoothing_lambda=smoothing_lambda,
            texture_bake=texture_bake,
        )

        return {"job_id": job_id, "status": "queued"}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status/{job_id}")
async def get_status(job_id: str):
    job = _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/jobs")
async def list_jobs(limit: int = 25):
    return _list_jobs(limit=limit)


@app.get("/result/{job_id}")
async def get_result(job_id: str):
    job = _get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.get("status") != "complete":
        raise HTTPException(status_code=409, detail="Result not ready")

    output_glb_path = job.get("output")
    if not output_glb_path or not os.path.exists(output_glb_path):
        raise HTTPException(status_code=404, detail="Output missing")

    return FileResponse(
        output_glb_path,
        media_type="model/gltf-binary",
        filename=f"model_{job_id}.glb",
    )

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
