# Handoff Document: Apex 3D AI Engine

## 🚀 Current Project State
The project is a fully functional, local 3D model generation tool using the **TripoSR** model by Stability AI. It features a premium, glassmorphism-style web interface and a FastAPI backend.

### ✅ Recent Enhancements (2026-02-06)
- **Async Job Pipeline**: Added `/generate_async`, `/status/{job_id}`, `/result/{job_id}`, and `/jobs` for background processing and job history.
- **Job Persistence**: Job history is persisted to `outputs/jobs.json` and restored on startup.
- **Premium Controls**: Added quality presets (Fast/Balanced/Quality), density threshold slider, and smoothing options in the UI.
- **Multi-Image Input**: Backend and UI now accept multiple images (2–4 recommended) for better reconstruction.
- **Texture Bake Toggle**: Experimental `texture_bake` flag added end-to-end with safe fallback when deps are missing.

### Key Accomplishments:
- **UI/UX**: Implemented a modern, high-fidelity dark theme with a drag-and-drop upload zone and a responsive 3D viewer.
- **3D Realism**: 
  - Upgraded mesh extraction resolution to **512**.
  - Integrated **Laplacian smoothing** via `trimesh` to remove marching cubes artifacts.
  - Configured high-fidelity rendering in `model-viewer` (soft shadows, HDR exposure, neutral tone-mapping).
- **Interaction Logic**: Corrected rotation axes and implemented an intuitive "drag-to-rotate" model.
- **Backend Stability**: Ensured robust CPU fallback for environments without CUDA and optimized image preprocessing.

## 🛠 Technical Architecture
- **Frontend**: Single-page application using `@google/model-viewer` for 3D rendering.
- **Backend**: FastAPI (`app.py`) serving as a REST API for image processing and 3D generation.
- **Engine**: TripoSR-based generation (`engine.py`) with `rembg` for background removal.

### Critical Tuning Parameters (`engine.py`):
- `resolution=256|512`: Adjustable via UI preset (512 for fidelity).
- `threshold=15..45`: Density threshold (default 30.0).
- `iterations=8|15|25, lamb=0.1..0.15`: Smoothing settings driven by UI (low/medium/high).

### Viewer Settings (`static/index.html`):
- `exposure="0.8"`: Balanced to prevent color washout on 3D models.
- `shadow-intensity="0.4"`: Soft shadows to provide depth without dark artifacts.
- `orbit-sensitivity="-1"`: Ensures interaction follows the "swipe" intuition.

## 📌 Known Limitations
- **Generation Time**: Currently running on CPU, which takes ~30-60 seconds per model.
- **Texture Resolution**: The vertex-color approach has limitations for complex patterns; full texture baking requires specific C++ dependencies (`xatlas`, `moderngl`) and a complete baking pipeline.
- **Multi-View Assumption**: Current multi-image path calls TripoSR with a list of images; if the model expects a different API, adjust `engine.py` accordingly.

## 🔮 Future Roadmap & Next Steps
1. **Texture Baking v1**: Implement a real `xatlas` + `moderngl` pipeline (UV unwrap + raster bake).
2. **Multi-View Conditioning**: Confirm TripoSR’s multi-view API and adapt input pipeline if required.
3. **PBR Materials**: Research ways to map image material properties (glossiness, metallic) to the 3D model’s PBR materials.
4. **Performance**: Investigate OpenVINO or ONNX optimizations for TripoSR to speed up CPU inference.

## 🏃 Keeping the Server Running
To start the engine locally:
```powershell
.\venv\Scripts\python.exe app.py
```
Access the UI at `http://localhost:8000`.

---
*Updated on 2026-02-06*
