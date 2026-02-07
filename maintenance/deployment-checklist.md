# Deployment Checklist - Lunar Nova 3D Engine

Use this checklist before every deployment to production/main branch.

---

## Pre-Deployment Checks

### Code Quality
- [ ] All Python files pass syntax check: `python -m py_compile app.py engine.py`
- [ ] No obvious typos or debug code left in
- [ ] All imports resolve: `python -c "import app; import engine"`
- [ ] No hardcoded paths or credentials
- [ ] Debug print statements removed (or converted to proper logging)

### Environment
- [ ] Virtual environment activated: `.\venv\Scripts\activate`
- [ ] Dependencies up to date: `pip list` matches `requirements.txt`
- [ ] If dependencies changed, `requirements.txt` updated: `pip freeze > requirements.txt`
- [ ] Python version compatible (3.8+)

### Functionality Testing
- [ ] Server starts without errors: `python app.py`
- [ ] Engine loads successfully (see "Model initialized." message)
- [ ] CUDA status checked: `python -c "import torch; print(torch.cuda.is_available())"`
- [ ] Test single-image generation:
  - [ ] Upload PNG image
  - [ ] Generation completes successfully
  - [ ] GLB file downloads
  - [ ] Model renders in 3D viewer
- [ ] Test multi-image generation (2-4 images)
- [ ] Test quality presets (Fast, Balanced, Quality)
- [ ] Test smoothing options (None, Low, Medium, High)
- [ ] If texture baking available, test with toggle enabled

### Async/Job Queue Testing
- [ ] Test `/generate_async` endpoint
- [ ] Job status updates correctly: `/status/{job_id}`
- [ ] Job completes and result downloadable: `/result/{job_id}`
- [ ] Job history visible: `/jobs`
- [ ] `outputs/jobs.json` updates correctly

### Edge Cases
- [ ] Test with very large image (>4K)
- [ ] Test with small image (<512px)
- [ ] Test with transparent PNG
- [ ] Test with JPEG
- [ ] Test error handling (upload invalid file type)
- [ ] Test server behavior when disk space low

### API Testing (if changes affect endpoints)
- [ ] Test all modified endpoints with Postman/curl
- [ ] Verify HTTP status codes correct (200, 400, 404, 500)
- [ ] Check JSON response format matches documentation
- [ ] Verify error messages are helpful and not exposing internals

### Performance
- [ ] Generation time reasonable (baseline: 30-60s CPU, 5-15s GPU)
- [ ] Memory usage stable during generation
- [ ] No memory leaks after multiple generations
- [ ] Server remains responsive during generation
- [ ] Concurrent requests handled gracefully (if using async)

### Code Review
- [ ] Review `git diff` carefully
- [ ] Only intended files modified
- [ ] No accidental deletions
- [ ] No large binary files committed (except necessary assets)
- [ ] Commit message follows format: `fix/feat/perf(component): description`

---

## Model-Specific Checks

### TripoSR Model
- [ ] Model files present in cache: `~/.cache/huggingface/hub/models--stabilityai--TripoSR/`
- [ ] Model loads without downloading (if not intentionally updating)
- [ ] Model version documented if changed

### Engine Parameters
- [ ] Resolution setting works (256, 512)
- [ ] Threshold range validated (0-100, typical 15-45)
- [ ] Smoothing parameters reasonable (iterations: 0-30, lambda: 0.05-0.2)
- [ ] Chunk size appropriate for available VRAM

---

## Documentation Checks

### Code Documentation
- [ ] New functions have docstrings
- [ ] Complex logic has explanatory comments
- [ ] Parameter types and return values documented

### User Documentation
- [ ] README.md updated if user-facing changes
- [ ] handoff.md updated if architecture changes
- [ ] API documentation current (if maintaining separate API docs)

### Operational Documentation
- [ ] CHANGELOG.md entry prepared (before commit)
- [ ] KNOWN_ISSUES.md reviewed and updated if fixing issues
- [ ] Bugfix document completed (if this is a bug fix)

---

## Git Workflow

### Before Commit
- [ ] Run: `git status` - verify correct files staged
- [ ] Run: `git diff --staged` - review all changes
- [ ] Remove any debugging code
- [ ] Ensure no sensitive data (API keys, etc.) in code

### Commit
- [ ] Use semantic commit message:
  ```
  fix(engine): handle CUDA OOM gracefully
  
  - Add try-except around torch operations
  - Fall back to CPU if VRAM insufficient
  - Add helpful error message for users
  
  Fixes issue in maintenance/bugfixes/2026-02-07_cuda-oom.md
  ```
- [ ] Commit only related changes together
- [ ] Use separate commits for separate concerns

### Push
- [ ] `git pull origin main` - ensure up to date
- [ ] Resolve any merge conflicts
- [ ] Test again after merge
- [ ] `git push origin main`

---

## Deployment (Server Restart)

### Preparation
- [ ] Note current server uptime
- [ ] Backup current `outputs/jobs.json` if critical

### Restart Procedure
- [ ] Stop current server:
  - **Interactive:** Ctrl+C
  - **Background:** `Stop-Process -Name python` (PowerShell)
  - **Service:** Restart service if configured
- [ ] Pull latest code: `git pull origin main`
- [ ] Reinstall dependencies if changed: `pip install -r requirements.txt`
- [ ] Start server: `.\venv\Scripts\python.exe app.py`
- [ ] Monitor startup logs for errors
- [ ] Verify "Model initialized." message

### Smoke Test (Immediately After Restart)
- [ ] Access UI: http://localhost:8000
- [ ] Page loads without errors
- [ ] Upload test image
- [ ] Generation completes successfully
- [ ] Download GLB file
- [ ] Check 3D viewer renders model

---

## Post-Deployment Monitoring

### First 5 Minutes
- [ ] Watch server logs for errors
- [ ] Test generation completes
- [ ] Check job queue functioning
- [ ] Verify `outputs/jobs.json` updating

### First Hour
- [ ] Monitor for crashes or hangs
- [ ] Check memory usage stable
- [ ] Verify multiple generations work

### Documentation Update
- [ ] Update CHANGELOG.md with deployment info:
  ```markdown
  ## [2026-02-07]
  ### Fixed
  - Handle CUDA OOM gracefully (commit abc123)
  ```
- [ ] Update KNOWN_ISSUES.md (mark resolved issues)
- [ ] Complete bugfix document with commit hash and deployment time
- [ ] Push documentation updates:
  ```bash
  git add CHANGELOG.md KNOWN_ISSUES.md maintenance/bugfixes/...
  git commit -m "docs: update after deployment"
  git push origin main
  ```

---

## Rollback Criteria

**Immediately rollback if:**
- Server crashes on startup
- All generations fail
- Critical error in logs
- Data corruption detected
- CUDA/model loading completely broken

**See:** [maintenance/rollback-procedures.md](rollback-procedures.md)

---

## Deployment Types

### Hotfix (Critical Bug)
- [ ] Follow abbreviated checklist (focus on fix testing)
- [ ] Test both before and after fix behavior
- [ ] Deploy ASAP, document fully afterward
- [ ] Mark commit with `hotfix(...)` prefix

### Feature Addition
- [ ] Follow full checklist
- [ ] Test new feature thoroughly
- [ ] Test that existing features still work (regression testing)
- [ ] Update user documentation
- [ ] Consider backward compatibility

### Dependency Update
- [ ] Test in isolated environment first
- [ ] Check for breaking changes in dependency
- [ ] Update `requirements.txt`
- [ ] Test all existing features work
- [ ] Document version change in CHANGELOG

### Configuration Change
- [ ] Document old and new values
- [ ] Test with new configuration
- [ ] Ensure values are appropriate for production
- [ ] Consider environment-specific configs

---

## Emergency Contact

**If deployment goes wrong:**
1. Check KNOWN_ISSUES.md for similar issues
2. Check maintenance/rollback-procedures.md
3. Review recent commits: `git log -5 --oneline`
4. Consider rollback if issue unclear
5. Document incident in new bugfix report

---

*Checklist Version: 1.0*  
*Last Updated: 2026-02-07*
