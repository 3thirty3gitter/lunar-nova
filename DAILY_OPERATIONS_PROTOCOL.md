# Daily Operations Protocol - Lunar Nova 3D Engine

**Reference this file at the start of every maintenance session.**

---

## SESSION START CHECKLIST

### 1. Review Current State
- [ ] Read `KNOWN_ISSUES.md` - check for open issues
- [ ] Read `CHANGELOG.md` - see recent changes
- [ ] Check `maintenance/bugfixes/` - review active bug reports
- [ ] Pull latest code: `git pull origin main`
- [ ] Check server logs for errors or crashes

### 2. Environment Check
- [ ] Verify Python virtual environment: `.\venv\Scripts\python.exe --version`
- [ ] Test server starts: `.\venv\Scripts\python.exe app.py` (should start without errors)
- [ ] Check CUDA availability: `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] Verify critical dependencies: `pip list | Select-String -Pattern "torch|trimesh|rembg|fastapi"`
- [ ] Check disk space in `outputs/` directory (3D models accumulate)
- [ ] Review `outputs/jobs.json` for any stuck or failed jobs

### 3. Engine Health Check
- [ ] Verify TripoSR model files present in cache (`~/.cache/huggingface/`)
- [ ] Test single-image generation (upload test image, verify .glb output)
- [ ] Check 3D viewer loads models correctly at http://localhost:8000
- [ ] Verify background removal (rembg) is working
- [ ] Test multi-image input (2-4 images)
- [ ] If texture baking enabled, verify xatlas/moderngl available

### 4. Session Context
- [ ] What are you working on today? (Bug fix / Feature / Investigation / Performance)
- [ ] Priority level? (Critical / High / Medium / Low)
- [ ] Expected timeline? (Minutes / Hours / Days)

---

## BUG REPORTING WORKFLOW

### When Bug is Discovered

1. **Document Immediately**
   ```powershell
   # Create new bugfix document
   $date = Get-Date -Format "yyyy-MM-dd"
   New-Item "maintenance/bugfixes/${date}_brief-description.md"
   ```

2. **Fill Out Bug Template**
   ```markdown
   # Bug: [Brief Description]
   
   **Date Discovered:** YYYY-MM-DD HH:MM
   **Severity:** Critical / High / Medium / Low
   **Reported By:** [Name/Role]
   **Environment:** Production Server / Dev / Testing
   
   ## Description
   Clear description of what's wrong.
   
   ## Steps to Reproduce
   1. Start server with...
   2. Upload image...
   3. See error...
   
   ## Expected Behavior
   What should happen.
   
   ## Actual Behavior
   What actually happens.
   
   ## Impact
   Who/what is affected? (All users / Specific features / Performance)
   
   ## Error Messages/Logs
   [Paste Python traceback, server logs, browser console errors]
   
   ## System Info
   - OS: Windows/Linux
   - Python version:
   - CUDA available: Yes/No
   - Affected endpoint: /generate, /generate_async, etc.
   
   ## Root Cause
   [Fill in after investigation]
   
   ## Fix Applied
   [Fill in after fix]
   
   ## Commit Hash
   [Fill in after deployment]
   
   ## Testing Done
   [Fill in after verification]
   
   ## Deployment
   Date/time pushed and server restarted.
   ```

3. **Update KNOWN_ISSUES.md**
   ```markdown
   ## Critical (or appropriate section)
   - [ ] Brief description - see maintenance/bugfixes/YYYY-MM-DD_name.md
   ```

---

## FIX IMPLEMENTATION PROTOCOL

### Before Coding

1. **Understand the Problem**
   - [ ] Can you reproduce the bug?
   - [ ] Do you understand the root cause?
   - [ ] Have you checked similar code for the same issue?
   - [ ] Is it a Python import issue, model loading issue, or generation issue?

2. **Plan the Fix**
   - [ ] What files need to be modified? (`app.py`, `engine.py`, `static/index.html`)
   - [ ] Will this break anything else?
   - [ ] Is this a surgical fix or does it require refactoring?
   - [ ] Do you need to update dependencies in `requirements.txt`?

3. **Surgical Changes Only**
   - [ ] Only touch what's needed
   - [ ] NO cleanup or refactoring unless requested
   - [ ] Maintain existing code patterns
   - [ ] Test in isolated environment first

### During Coding

1. **Make Surgical Changes**
   - Identify exact lines that need modification
   - Change ONLY those lines
   - Test incrementally
   - Keep error handling robust (try/except with meaningful messages)

2. **Test Locally**
   ```powershell
   # Restart server
   .\venv\Scripts\python.exe app.py
   
   # Test specific endpoint
   # Upload test image via UI at http://localhost:8000
   # Or use curl/Postman to test API directly
   
   # Check server logs for errors
   ```

3. **Verify Related Features**
   - Test features that use the same code
   - Check for regression issues:
     - Single image generation
     - Multi-image generation
     - Async job queue
     - Job history retrieval
     - Texture baking (if enabled)
     - 3D model viewer

4. **Engine-Specific Tests**
   - [ ] Background removal works (rembg)
   - [ ] Mesh extraction completes (TripoSR)
   - [ ] Smoothing applies correctly (trimesh)
   - [ ] GLB file exports successfully
   - [ ] 3D viewer renders model
   - [ ] Vertex colors preserved
   - [ ] Texture baking (if requested) doesn't crash

---

## DEPLOYMENT PROTOCOL

### Pre-Deployment

**ALWAYS follow `maintenance/deployment-checklist.md`**

Critical items:
- [ ] Python imports work: `python -c "import app; import engine"`
- [ ] Test the specific fix with real image uploads
- [ ] Check related features still work
- [ ] Review `git diff` - only intended changes
- [ ] Remove debug print statements (or convert to logging)
- [ ] Use proper commit message format
- [ ] Verify `requirements.txt` updated if dependencies changed
- [ ] Test with both CUDA and CPU modes (if applicable)

### Commit Message Format

```
fix(component): brief description of what was fixed

Detailed explanation if needed.
Addresses issue in maintenance/bugfixes/YYYY-MM-DD_name.md

Commit includes:
- What changed
- Why it changed
- Impact of change
```

Examples:
- `fix(engine): add fallback for TripoSR multi-view API compatibility`
- `fix(app): prevent job queue deadlock with proper threading`
- `hotfix(deps): pin rembg version to prevent segfault`
- `feat(texture): implement xatlas UV unwrapping for texture baking`
- `perf(engine): reduce VRAM usage with smaller chunk size`

### Deploy

```powershell
git add [files]
git commit -m "fix(component): description"
git push origin main

# If running as service, restart server:
# Option 1: Kill and restart manually
# Option 2: Use process manager (PM2, systemd, etc.)
# Option 3: Windows Service restart
```

### Post-Deployment

1. **Restart Server**
   - [ ] Stop current server process (Ctrl+C or kill process)
   - [ ] Start server: `.\venv\Scripts\python.exe app.py`
   - [ ] Verify server starts without errors
   - [ ] Check engine loads successfully ("Model initialized." message)

2. **Immediate Testing**
   - [ ] Access UI at http://localhost:8000
   - [ ] Test the fixed feature
   - [ ] Upload test image and verify generation
   - [ ] Check job history (/jobs endpoint)
   - [ ] Review server logs for first 5 minutes
   - [ ] Verify `outputs/jobs.json` updates correctly

3. **Verify 3D Output Quality**
   - [ ] .glb file downloads successfully
   - [ ] Model loads in 3D viewer without errors
   - [ ] Geometry looks correct (no artifacts)
   - [ ] Colors/textures preserved
   - [ ] File size reasonable (not corrupt or empty)

4. **Performance Check**
   - [ ] Generation time acceptable (30-60s CPU, 5-15s GPU)
   - [ ] Memory usage stable (no leaks)
   - [ ] Server responsive to new requests
   - [ ] Background jobs process correctly

---

## DOCUMENTATION UPDATE PROTOCOL

### After Successful Deployment

1. **Update CHANGELOG.md**
   ```markdown
   ## [YYYY-MM-DD]
   
   ### Fixed
   - Brief description (commit hash)
   ```

2. **Update KNOWN_ISSUES.md**
   - Mark issue as resolved
   - Remove from "In Progress" or "Critical"
   - Add to "Resolved" section if needed

3. **Complete Bugfix Document**
   - [ ] Add final commit hash
   - [ ] Document testing done
   - [ ] Add deployment timestamp
   - [ ] Note any follow-up needed

4. **Update handoff.md** (if significant changes)
   - Update current project state
   - Document new features or major fixes
   - Update known limitations
   - Revise roadmap if priorities changed

---

## EMERGENCY ROLLBACK PROTOCOL

**If critical issue discovered after deployment:**

1. **Assess Severity**
   - Is server crashing?
   - Are all generations failing?
   - Is CUDA/model loading broken?
   - Are users experiencing data loss?

2. **Immediate Action**
   - Stop the server immediately if data at risk
   - Check if rolling back code will fix it, or if it's a model cache issue

3. **Execute Rollback**
   ```powershell
   # Quick rollback (last commit)
   git revert HEAD
   git push origin main
   
   # Or see maintenance/rollback-procedures.md for other methods
   
   # Restart server with rollback
   .\venv\Scripts\python.exe app.py
   ```

4. **Model Cache Rollback** (if model files corrupted)
   ```powershell
   # Clear HuggingFace cache
   Remove-Item -Recurse -Force ~\.cache\huggingface\hub\models--stabilityai--TripoSR
   
   # Restart will re-download model
   ```

5. **Document Incident**
   - Update KNOWN_ISSUES.md
   - Create incident report in bugfix doc
   - Note time of failure and rollback

6. **Fix Properly**
   - Investigate in dev environment
   - Test thoroughly with various images
   - Test both CUDA and CPU modes
   - Redeploy when confident

---

## SESSION END CHECKLIST

Before ending your session:

- [ ] All changes committed and pushed?
- [ ] CHANGELOG.md updated?
- [ ] KNOWN_ISSUES.md updated?
- [ ] Bugfix documents completed?
- [ ] Server running and verified working?
- [ ] Any follow-up tasks documented?
- [ ] Server logs reviewed for new errors?
- [ ] Test generation completed successfully?
- [ ] Virtual environment properly activated for next session?
- [ ] No stray Python processes left running?

---

## QUICK REFERENCE

**Files to check at session start:**
- `KNOWN_ISSUES.md`
- `CHANGELOG.md`
- `maintenance/bugfixes/`
- `outputs/jobs.json`

**Files to update after deployment:**
- `CHANGELOG.md`
- `KNOWN_ISSUES.md`
- Bugfix document with commit hash
- `handoff.md` (if major changes)

**Emergency procedures:**
- `maintenance/rollback-procedures.md`

**Deployment checklist:**
- `maintenance/deployment-checklist.md`

**Critical files:**
- `app.py` - FastAPI server & endpoints
- `engine.py` - TripoSR 3D generation engine
- `static/index.html` - Web UI
- `requirements.txt` - Python dependencies

**Output directories:**
- `outputs/` - Generated .glb files
- `outputs/jobs.json` - Job persistence
- `temp_inputs/` - Uploaded images (cleaned after processing)

**Model paths:**
- `TripoSR/` - TripoSR model code
- `~/.cache/huggingface/` - Downloaded model weights

---

## COMMON SCENARIOS

### Scenario 1: TripoSR Model Loading Failure

**Symptoms:** Server crashes on startup, "Cannot import TSR" error

**Investigation:**
1. Check TripoSR repo cloned: `ls TripoSR/tsr/`
2. Verify Python path includes TripoSR: check `engine.py` sys.path
3. Check model files: `ls ~/.cache/huggingface/hub/models--stabilityai--TripoSR/`
4. Test import: `python -c "from tsr.system import TSR"`

**Common Fixes:**
- Re-clone TripoSR: `git clone https://github.com/VAST-AI-Research/TripoSR.git`
- Clear cache and re-download: `rm -r ~/.cache/huggingface/`
- Check network connectivity for model download
- Verify disk space available

### Scenario 2: Generation Fails with "CUDA out of memory"

**Symptoms:** First generation works, subsequent ones fail with OOM

**Investigation:**
1. Check VRAM usage: `nvidia-smi`
2. Review chunk size setting in `engine.py`
3. Check if model is being released properly between generations

**Common Fixes:**
```python
# In engine.py, reduce chunk size
self.model.renderer.set_chunk_size(4096)  # Lower from 8192

# Or force CPU mode
engine = Local3DEngine(device="cpu")

# Add torch.cuda.empty_cache() after generation
```

### Scenario 3: Background Removal (rembg) Fails

**Symptoms:** Generation fails early, "rembg session error"

**Investigation:**
1. Test rembg separately: `python -c "import rembg; rembg.new_session()"`
2. Check model downloads for rembg (u2net models)
3. Review error logs for network issues

**Common Fixes:**
- Reinstall rembg: `pip install --force-reinstall rembg`
- Clear rembg cache
- Check firewall/network settings

### Scenario 4: Texture Baking Fails

**Symptoms:** "Texture baking requested but optional deps are missing"

**Investigation:**
1. Check xatlas installed: `pip show xatlas`
2. Check moderngl installed: `pip show moderngl`
3. Verify OpenGL context available (requires display or headless GL)

**Common Fixes:**
```powershell
# Install texture baking dependencies
pip install xatlas moderngl

# For headless servers, install EGL
# Linux: apt-get install libegl1-mesa
# Windows: Usually works, check GPU drivers
```

### Scenario 5: Mesh Quality Issues

**Symptoms:** Model has artifacts, holes, or poor quality

**Investigation:**
1. Check input image quality (resolution, clarity)
2. Review edge extraction (density threshold)
3. Check if smoothing is applied

**Tuning:**
```python
# In app.py or via UI controls
resolution=512  # Higher = better quality, slower
threshold=25.0  # Lower = more geometry, higher = cleaner
smoothing="high"  # More smoothing removes artifacts
```

### Scenario 6: Server Hangs on Generation

**Symptoms:** Request never completes, server non-responsive

**Investigation:**
1. Check if process is using CPU/GPU (might just be slow)
2. Review logs for deadlocks
3. Check if async job queue is stuck

**Common Fixes:**
- Restart server
- Review threading/async implementation
- Add timeout to generation: `asyncio.wait_for(generation, timeout=180)`
- Check if jobs.json file is locked

### Scenario 7: Multi-View Input Fails

**Symptoms:** "Multi-view inputs are not supported" error

**Investigation:**
1. Check TripoSR version/build
2. Review engine.py fallback logic
3. Test with single image first

**Common Fixes:**
```powershell
# Set environment variable to use first image only
$env:TRIPOSR_MULTIVIEW_FALLBACK="first"
.\venv\Scripts\python.exe app.py

# Or update TripoSR to version that supports multi-view
```

---

## TESTING CHECKLIST

### Basic Functionality Test
- [ ] Server starts without errors
- [ ] UI loads at http://localhost:8000
- [ ] Single image upload works
- [ ] 3D preview displays model
- [ ] GLB download works
- [ ] Model opens in external viewer (Blender, etc.)

### Advanced Functionality Test
- [ ] Multi-image upload (2-4 images)
- [ ] Quality preset changes (Fast/Balanced/Quality)
- [ ] Density threshold adjustment
- [ ] Smoothing options (None/Low/Medium/High)
- [ ] Async generation (/generate_async endpoint)
- [ ] Job status polling (/status/{job_id})
- [ ] Job history (/jobs)
- [ ] Texture baking toggle (if deps available)

### Edge Cases
- [ ] Very large image (>4K resolution)
- [ ] Very small image (<256px)
- [ ] Transparent PNG
- [ ] JPEG with EXIF rotation
- [ ] Grayscale image
- [ ] Image with complex background
- [ ] Multiple objects in image
- [ ] Very dark or very bright image

### Performance Test
- [ ] Single generation time logged
- [ ] Consecutive generations (check for memory leaks)
- [ ] Concurrent requests (if async queue)
- [ ] Large batch test (10+ images in sequence)

---

**END OF PROTOCOL**

Always prioritize: **Data Integrity > Stability > Performance > Features**

---

*Last Updated: 2026-02-07*
