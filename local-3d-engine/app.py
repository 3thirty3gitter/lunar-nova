from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import shutil
import os
import uuid
from engine import get_engine

app = FastAPI(title="Local 3D AI Engine")

# Directories
TEMP_DIR = "temp_inputs"
OUTPUT_DIR = "outputs"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("Loading engine... (this may take a moment)")
# Pre-load engine on startup
engine = get_engine()

@app.post("/generate")
async def generate_3d(file: UploadFile = File(...)):
    """
    Standard endpoint: Upload image, get 3D model (GLB) back.
    """
    try:
        # Save input file
        file_ext = file.filename.split(".")[-1]
        unique_id = str(uuid.uuid4())
        input_filename = f"{unique_id}.{file_ext}"
        input_path = os.path.join(TEMP_DIR, input_filename)
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Generate
        # Create a unique output folder for this run
        run_output_dir = os.path.join(OUTPUT_DIR, unique_id)
        
        output_glb_path = engine.generate(input_path, run_output_dir)
        
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
