# Rollback Procedures - Lunar Nova 3D Engine

This document describes various rollback procedures for when deployments go wrong.

---

## When to Rollback

### Immediate Rollback Scenarios
- Server crashes on startup
- All 3D generations fail
- Critical Python import errors
- Model loading completely broken
- Data corruption detected (jobs.json)
- CUDA errors preventing any operation

### Consider Hotfix Instead
- Single feature broken, others work fine
- Minor visual bug
- Performance degradation but functional
- Non-critical endpoint failing

---

## Rollback Methods

### Method 1: Git Revert (Recommended)

**Use when:** Most recent commit caused the issue

**Advantages:**
- Preserves history
- Clear audit trail
- Can be reverted again if needed

**Procedure:**
```powershell
# 1. Stop the server
# Windows: Ctrl+C or Stop-Process

# 2. Revert the last commit
git revert HEAD

# This creates a new commit undoing the changes
# Git will open an editor for commit message
# Default message is usually fine: "Revert '[original commit message]'"

# 3. Push the revert
git push origin main

# 4. Restart server
.\venv\Scripts\python.exe app.py

# 5. Verify server starts correctly
# 6. Test basic generation

# 7. Document incident
# Update KNOWN_ISSUES.md with what happened and when
```

**Multiple Commits:**
```powershell
# If last 3 commits are bad:
git revert HEAD~2..HEAD

# Or individually:
git revert <commit-hash-3>
git revert <commit-hash-2>
git revert <commit-hash-1>
```

---

### Method 2: Reset to Last Known Good State

**Use when:** Multiple recent commits are problematic and you want a clean state

**Advantages:**
- Quick recovery
- Clean slate

**Disadvantages:**
- Loses commit history (must force push)
- More disruptive

**Procedure:**
```powershell
# 1. Stop the server

# 2. Find last known good commit
git log --oneline
# Find the commit hash that was working

# 3. BACKUP current state (optional but recommended)
git branch backup-before-reset

# 4. Reset to good commit
git reset --hard <good-commit-hash>

# 5. Force push (CAUTION: rewrites history)
git push --force origin main

# 6. Restart server
.\venv\Scripts\python.exe app.py

# 7. Verify and document
```

⚠️  **Warning:** Only use `--force` if you're the only developer or team is coordinated!

---

### Method 3: Dependency Rollback

**Use when:** Dependency update caused the issue

**Procedure:**
```powershell
# 1. Stop server

# 2. Check git history for requirements.txt changes
git log -p requirements.txt

# 3. Revert to previous requirements.txt
git checkout HEAD~1 -- requirements.txt

# 4. Reinstall dependencies
pip install -r requirements.txt

# 5. Test if this fixes the issue
.\venv\Scripts\python.exe app.py

# 6. If works, commit the requirements.txt restore
git add requirements.txt
git commit -m "fix(deps): rollback dependencies to resolve [issue]"
git push origin main

# 7. Document which dependency caused issue and why
```

---

### Method 4: Model Cache Rollback

**Use when:** Model files corrupted or wrong version loaded

**Procedure:**
```powershell
# 1. Stop server

# 2. Clear HuggingFace cache (will require re-download)
Remove-Item -Recurse -Force ~\.cache\huggingface\hub\models--stabilityai--TripoSR

# 3. Optionally, clear entire cache (nuclear option)
# Remove-Item -Recurse -Force ~\.cache\huggingface\

# 4. Restart server (will re-download model during startup)
.\venv\Scripts\python.exe app.py

# This will take time for model download (2-3GB)
# Ensure good network connection

# 5. Verify model loads correctly
# Check "Model initialized." message
# Test generation
```

**Disk Space Issue:**
If cache is on different drive and full:
```powershell
# Set HuggingFace cache to different location
$env:HF_HOME="D:\huggingface_cache"
$env:TRANSFORMERS_CACHE="D:\huggingface_cache"

.\venv\Scripts\python.exe app.py
```

---

### Method 5: Virtual Environment Rebuild

**Use when:** Python environment corrupted or dependencies conflict

**Procedure:**
```powershell
# 1. Stop server

# 2. Backup current environment (optional)
Rename-Item venv venv.old

# 3. Create fresh virtual environment
python -m venv venv

# 4. Activate new environment
.\venv\Scripts\activate

# 5. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 6. Test server start
python app.py

# 7. If works, remove old environment
Remove-Item -Recurse -Force venv.old

# 8. Document what was wrong with old environment
```

---

### Method 6: Job History Recovery

**Use when:** outputs/jobs.json corrupted or lost

**Procedure:**
```powershell
# 1. Stop server

# 2. Check if backup exists
Get-Item outputs/jobs.json.bak

# 3a. If backup exists, restore
Copy-Item outputs/jobs.json.bak outputs/jobs.json

# 3b. If no backup, restore empty state
echo '{}' > outputs/jobs.json

# Or restore from git history if tracked:
git checkout HEAD~1 -- outputs/jobs.json

# 4. Restart server
.\venv\Scripts\python.exe app.py

# 5. Verify job history loads correctly
# Check /jobs endpoint
```

**Prevent Future Issues:**
```powershell
# Add scheduled task to backup jobs.json
# Windows Task Scheduler:
# Create daily task running:
Copy-Item outputs/jobs.json outputs/jobs.json.bak
```

---

## Rollback Verification Checklist

After any rollback:

- [ ] Server starts without errors
- [ ] Engine loads successfully ("Model initialized." message)
- [ ] UI accessible at http://localhost:8000
- [ ] Single-image generation works
- [ ] Multi-image generation works (if supported in rolled-back version)
- [ ] Job queue functioning
- [ ] Job history accessible
- [ ] 3D viewer renders models
- [ ] No error spam in logs

---

## Post-Rollback Actions

### Immediate (within 1 hour)
1. **Document Incident**
   ```markdown
   # Incident Report: [Date/Time]
   
   ## What Happened
   - Deployment at [time] caused [issue]
   - Rolled back at [time] using [method]
   
   ## Impact
   - Server down for [duration]
   - [X] generations affected
   
   ## Root Cause
   - [Preliminary analysis]
   
   ## Rollback Method
   - Used git revert / reset / etc.
   - Commit hash rolled back to: [hash]
   
   ## Current State
   - Server stable
   - All tests passing
   ```

2. **Update KNOWN_ISSUES.md**
   - Add issue that caused rollback as Critical
   - Link to incident report

### Short Term (within 24 hours)
1. **Root Cause Analysis**
   - Investigate why deployment failed
   - Identify what was missed in pre-deployment testing
   - Document in bugfix report

2. **Create Fix**
   - Develop proper fix in dev environment
   - Test extensively
   - Follow full deployment checklist

3. **Improve Processes**
   - Add missing test case to deployment checklist
   - Update procedures to prevent recurrence
   - Consider additional safeguards

### Long Term
1. **Update Documentation**
   - Add scenario to DAILY_OPERATIONS_PROTOCOL.md
   - Update deployment checklist with new checks

2. **Consider Automation**
   - Add automated tests for this scenario
   - Consider CI/CD pipeline with pre-deployment tests

---

## Emergency Commands

**Critical Commands:**
```powershell
# Stop server (Windows)
Get-Process python | Where-Object {$_.Path -like "*lunar-nova*"} | Stop-Process

# Check what's running on port 8000
netstat -ano | findstr :8000

# Quick server restart
# Ctrl+C (if interactive)
.\venv\Scripts\python.exe app.py
```

**Quick Links:**
- [DAILY_OPERATIONS_PROTOCOL.md](../DAILY_OPERATIONS_PROTOCOL.md)
- [deployment-checklist.md](deployment-checklist.md)
- [KNOWN_ISSUES.md](../KNOWN_ISSUES.md)
- [CHANGELOG.md](../CHANGELOG.md)

**System Info:**
```powershell
# Python version
python --version

# Package versions
pip list

# Git status
git status
git log -5 --oneline

# Disk space
Get-PSDrive C

# Memory
Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory

# GPU
nvidia-smi              # If CUDA available
```

---

## Prevention Strategies

### Before Every Deployment
- Follow full deployment checklist
- Test in isolated environment
- Review git diff carefully
- Keep deployments small and focused

### Automated Safeguards
- Pre-commit hooks for syntax check: `python -m py_compile`
- pytest suite for critical functions
- Automated backup of jobs.json before restart

### Monitoring
- Log aggregation and monitoring
- Health check endpoint
- Alerting for server down (if critical)

---

*Last Updated: 2026-02-07*
