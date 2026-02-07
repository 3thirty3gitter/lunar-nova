# Known Issues - Lunar Nova 3D Engine

**Last Updated:** 2026-02-07

This document tracks known bugs, limitations, and issues in the Lunar Nova 3D Engine project.

---

## 🔴 Critical

*No critical issues at this time.*

---

## 🟠 High Priority

### Performance: CPU Generation Slow
- **Issue:** Generation takes 30-60 seconds per model on CPU
- **Impact:** Poor user experience, server can handle limited concurrent requests
- **Workaround:** Use CUDA-enabled GPU
- **Status:** Under investigation
- **Related:** Consider OpenVINO/ONNX optimization

### TripoSR: Module Not Found
- **Issue:** TripoSR module not installed, `from tsr.system import TSR` fails
- **Impact:** Engine cannot initialize, server won't start
- **Workaround:** Need to install or configure TripoSR properly
- **Status:** In Progress - Installation/configuration needed

---

## 🟡 Medium Priority

### Multi-View: API Compatibility Uncertain
- **Issue:** Current multi-image path assumes TripoSR accepts list of images, but API may differ
- **Impact:** Multi-view generation may not provide expected quality improvement
- **Workaround:** Environment variable `TRIPOSR_MULTIVIEW_FALLBACK=first` uses only first image
- **Status:** API detection implemented, needs testing with actual TripoSR installation

### Texture Baking: Optional Dependencies
- **Issue:** Texture baking requires `xatlas` and `moderngl` which may not install on all systems
- **Impact:** Texture baking feature unavailable without manual dependency installation
- **Workaround:** Feature gracefully degrades to vertex colors only
- **Status:** Documented in README, xatlas added to requirements.txt

### Texture Resolution: Vertex Color Limitations
- **Issue:** Vertex-color approach has limited fidelity for complex patterns
- **Impact:** Fine details and textures may appear blurred or low-quality
- **Workaround:** Use texture baking when available (now implemented)
- **Status:** Texture baking pipeline complete, testing needed

---

## 🟢 Low Priority

### UI: No Progress Indicator for Sync Endpoint
- **Issue:** `/generate` endpoint doesn't provide progress updates during generation
- **Impact:** User sees loading spinner with no feedback for 30-60 seconds
- **Workaround:** Use async endpoint `/generate_async` instead
- **Status:** Enhancement request

### Job History: No Pagination UI
- **Issue:** `/jobs` endpoint returns last 25 jobs, but no UI pagination
- **Impact:** Cannot browse full job history beyond 25 items
- **Workaround:** Query API directly with limit parameter
- **Status:** Enhancement request

### Cleanup: Temporary Files Accumulate
- **Issue:** `temp_inputs/` directory not always cleaned on error
- **Impact:** Disk space usage increases over time
- **Workaround:** Manual cleanup periodically
- **Status:** Low priority, add scheduled cleanup task

### VRAM: Memory Leak on Consecutive Generations
- **Issue:** VRAM not fully released between generations on some GPU configurations
- **Impact:** Eventually hits OOM after many generations
- **Workaround:** Restart server periodically, or reduce chunk size
- **Status:** Investigating proper cleanup in engine.py

---

## ⚪ Limitations (By Design)

### No Multi-User Support
- **Description:** Server is single-process, no authentication or multi-tenancy
- **Rationale:** Designed for local/single-user deployment
- **Future:** Consider Redis-based job queue for multi-worker setup

### No Input Validation
- **Description:** Minimal validation on uploaded images (size, format, content)
- **Rationale:** Trust local user input
- **Future:** Add basic size limits and format checks

### Model Cache Location
- **Description:** TripoSR models download to `~/.cache/huggingface/` (large, ~2GB)
- **Rationale:** HuggingFace Hub default behavior
- **Future:** Document how to change cache location via environment variable

### Windows-Specific Documentation
- **Description:** Some documentation and examples use PowerShell/Windows paths
- **Rationale:** Primary development on Windows
- **Future:** Add Linux/Mac equivalent commands where needed

---

## ✅ Resolved

### ~~Server Crash on Invalid Image~~ (Fixed 2026-02-06)
- **Fix:** Added proper error handling in preprocessing
- **Commit:** [See handoff.md]

### ~~3D Viewer Rotation Inverted~~ (Fixed 2026-02-06)
- **Fix:** Corrected orbit-sensitivity setting in model-viewer
- **Commit:** [See handoff.md]

---

## 📋 To Document

*Issues discovered but not yet fully documented here should be added immediately with at least:*
- Brief description
- Impact assessment
- Date discovered
- Link to bugfix document if created

---

*For reporting new issues, see [DAILY_OPERATIONS_PROTOCOL.md](DAILY_OPERATIONS_PROTOCOL.md#bug-reporting-workflow)*
