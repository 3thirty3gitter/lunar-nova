# Changelog - Lunar Nova 3D Engine

All notable changes to the Lunar Nova 3D Engine project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2026-02-07] - Operations Protocol Implementation

### Added
- Daily Operations Protocol adapted for AI engine operations (commit: 59c5013)
- Maintenance documentation structure (CHANGELOG, KNOWN_ISSUES, deployment procedures)
- Multi-view conditioning with fallback support
- Production-ready texture baking pipeline with xatlas + moderngl
- Bug tracking workflow in maintenance/bugfixes/
- Deployment checklist and rollback procedures

### Changed
- Updated documentation structure for local AI engine development
- Engine now probes model API for multi-view compatibility
- Handoff.md updated with setup instructions and current state

### Deployment
- **Committed**: 2026-02-07
- **Commit Hash**: 59c5013
- **Status**: Code ready, environment setup required for first run

---

## [2026-02-06] - Major Enhancement Release

### Added
- **Async Job Pipeline**: New endpoints `/generate_async`, `/status/{job_id}`, `/result/{job_id}`, `/jobs` for background processing
- **Job Persistence**: Job history now persisted to `outputs/jobs.json` and restored on server startup
- **Premium Controls**: Quality presets (Fast/Balanced/Quality), density threshold slider, smoothing options
- **Multi-Image Input**: Backend and UI now accept multiple images (2–4 recommended) for better reconstruction
- **Texture Bake Toggle**: Experimental `texture_bake` flag with safe fallback when dependencies missing

### Changed
- Upgraded mesh extraction resolution to 512 for higher fidelity
- Improved 3D viewer rendering with soft shadows and HDR exposure
- Corrected rotation axes for intuitive "drag-to-rotate" interaction

### Fixed
- CPU fallback now works correctly when CUDA unavailable
- Image preprocessing handles edge cases better

---

## [2026-02-05] - UI/UX Improvements

### Added
- Modern glassmorphism-style dark theme web interface
- Drag-and-drop upload zone
- Responsive 3D viewer using `@google/model-viewer`

### Changed
- Integrated Laplacian smoothing via trimesh to remove marching cubes artifacts
- Configured high-fidelity rendering in model-viewer

---

## [2026-02-04] - Core Engine Implementation

### Added
- FastAPI backend (`app.py`) serving REST API
- TripoSR-based generation engine (`engine.py`)
- rembg integration for background removal
- Basic mesh export to GLB format

### Technical Details
- Initial resolution set to 256
- Default threshold: 30.0
- Basic smoothing: 15 iterations, lambda 0.1

---

## [Unreleased]

### Planned
- PBR material mapping from image properties
- Performance optimization via OpenVINO or ONNX
- CUDA optimization for faster generation
- Batch processing capabilities
- Job queue management UI
- Model gallery/history viewer
- Advanced post-processing options

---

*Generated: 2026-02-07*
