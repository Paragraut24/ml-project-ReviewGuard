# Pre-Commit Security Checklist

**⚠️ CRITICAL: Complete this checklist before pushing to GitHub!**

## 🔒 Security Verification

### 1. Environment Variables & Secrets

- [ ] `.env` file is NOT committed (check with `git status`)
- [ ] `.env.example` exists with placeholder values only
- [ ] No API keys, tokens, or passwords in any files
- [ ] `SECRET_KEY` is not hardcoded anywhere
- [ ] `HF_TOKEN` is not in any committed files
- [ ] No database credentials in code

**Verify:**
```bash
# Search for potential secrets
grep -r "hf_" . --exclude-dir=.git --exclude-dir=.venv
grep -r "sk-" . --exclude-dir=.git --exclude-dir=.venv
grep -r "password" . --exclude-dir=.git --exclude-dir=.venv
grep -r "secret" . --exclude-dir=.git --exclude-dir=.venv
```

### 2. Sensitive Files Removed

- [ ] No training scripts (`train_*.py`, `evaluate_*.py`)
- [ ] No test files (`test_*.py`)
- [ ] No development notebooks (`*.ipynb`)
- [ ] No raw data files (`*.csv`, `*.json` with data)
- [ ] No implementation docs (`*_IMPLEMENTATION.md`)
- [ ] No backup files (`*.bak`, `*.backup`, `OLD_*`)
- [ ] No personal notes or TODO files

**Verify:**
```bash
# Check for files that shouldn't be committed
git status
git ls-files | grep -E "(train_|test_|evaluate_|\.ipynb|\.csv|IMPLEMENTATION)"
```

### 3. .gitignore Configuration

- [ ] `.gitignore` file exists and is comprehensive
- [ ] `.env` is in `.gitignore`
- [ ] `__pycache__/` is in `.gitignore`
- [ ] `.venv/` and `venv/` are in `.gitignore`
- [ ] Training data directories are in `.gitignore`
- [ ] IDE-specific files are in `.gitignore`

**Verify:**
```bash
# Test .gitignore
git check-ignore .env
git check-ignore __pycache__
git check-ignore .venv
```

### 4. Code References

- [ ] No "college project" mentions anywhere
- [ ] No "ML project" references
- [ ] No "assignment" or "homework" mentions
- [ ] No professor or course names
- [ ] No academic references in comments
- [ ] Footer text updated (no "ML Project 2026")

**Verify:**
```bash
# Search for academic references
grep -ri "college" . --exclude-dir=.git --exclude-dir=.venv
grep -ri "ml project" . --exclude-dir=.git --exclude-dir=.venv
grep -ri "assignment" . --exclude-dir=.git --exclude-dir=.venv
```

### 5. Documentation

- [ ] `README.md` is professional and complete
- [ ] `LICENSE` file exists with restrictive terms
- [ ] `SECURITY.md` exists
- [ ] `CONTRIBUTING.md` exists
- [ ] `DEPLOYMENT.md` exists
- [ ] `.env.example` exists
- [ ] No internal documentation committed

### 6. Code Quality

- [ ] No debug `print()` statements in production code
- [ ] No commented-out code blocks
- [ ] No TODO comments with sensitive information
- [ ] No hardcoded file paths (use relative paths)
- [ ] No localhost URLs in production code

**Verify:**
```bash
# Check for debug statements
grep -r "print(" . --include="*.py" --exclude-dir=.git --exclude-dir=.venv
grep -r "console.log" . --include="*.js" --exclude-dir=.git
```

### 7. Dependencies

- [ ] `requirements.txt` contains only production dependencies
- [ ] No development-only packages in `requirements.txt`
- [ ] `requirements.local-ml.txt` is in `.gitignore` (if exists)
- [ ] All dependencies are pinned to specific versions
- [ ] No vulnerable dependencies (run `pip-audit` if available)

**Verify:**
```bash
# Check requirements
cat requirements.txt
# Should NOT contain: jupyter, notebook, pytest, black, flake8, etc.
```

### 8. Model Files

- [ ] BERT model is hosted on HuggingFace (not in repo)
- [ ] GNN model files are necessary and minimal
- [ ] No training checkpoints committed
- [ ] No large model files (>100MB) in repo
- [ ] Model files are in `.gitignore` if not needed

**Verify:**
```bash
# Check for large files
find . -type f -size +10M -not -path "./.git/*" -not -path "./.venv/*"
```

### 9. Configuration Files

- [ ] `Procfile` exists for Heroku deployment
- [ ] `render.yaml` exists for Render deployment
- [ ] `runtime.txt` specifies Python version
- [ ] No sensitive configuration in `render.yaml`
- [ ] All config files use environment variables

### 10. Git History

- [ ] No sensitive data in previous commits
- [ ] No large files in git history
- [ ] Commit messages are professional
- [ ] No personal information in commits

**Verify:**
```bash
# Check git history for secrets
git log --all --full-history --source -- .env
git log --all --full-history --source -- *secret*
```

## 📝 Final Checks

### Repository Structure

Expected structure:
```
reviewguard/
├── .gitignore
├── .env.example
├── LICENSE
├── README.md
├── SECURITY.md
├── CONTRIBUTING.md
├── DEPLOYMENT.md
├── requirements.txt
├── runtime.txt
├── Procfile
├── render.yaml
├── app.py
├── gnn_inference.py
├── gnn_model_weighted.pt
├── graph_data.pt
├── scaler.pkl
├── bert_model/
│   ├── config.json
│   ├── tokenizer.json
│   └── tokenizer_config.json
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── app.js
│   ├── confusion_matrix.png
│   └── accuracy_chart.png
└── templates/
    ├── landing.html
    ├── index.html
    ├── reports.html
    ├── docs.html
    └── settings.html
```

### Files That Should NOT Be Present

- ❌ `.env`
- ❌ `*.ipynb`
- ❌ `train_*.py`
- ❌ `test_*.py`
- ❌ `evaluate_*.py`
- ❌ `*.csv` (data files)
- ❌ `*_IMPLEMENTATION.md`
- ❌ `*.bak`, `*.backup`
- ❌ `__pycache__/`
- ❌ `.venv/`, `venv/`

### Pre-Push Commands

Run these commands before pushing:

```bash
# 1. Check git status
git status

# 2. Review changes
git diff

# 3. Check for secrets
git secrets --scan  # If git-secrets is installed

# 4. Verify .gitignore
git check-ignore -v .env

# 5. Test locally
python app.py
# Visit http://localhost:5000 and test all pages

# 6. Check for large files
git ls-files | xargs ls -lh | sort -k5 -h -r | head -20

# 7. Verify no secrets in staged files
git diff --cached | grep -i "secret\|password\|token\|key"
```

## 🚀 Ready to Push

Once all checks pass:

```bash
# Stage files
git add .

# Commit with professional message
git commit -m "Initial commit: ReviewGuard v4.2.0 - AI-powered review fraud detection"

# Push to GitHub
git push origin main
```

## ⚠️ If You Find Issues

### If Secrets Were Committed

1. **DO NOT PUSH!**
2. Remove from staging: `git reset HEAD <file>`
3. Add to `.gitignore`
4. Commit again

### If Secrets Are in History

1. Use `git filter-branch` or `BFG Repo-Cleaner`
2. Force push (if repo is private)
3. Rotate all exposed secrets immediately

### If Large Files Were Committed

1. Remove from staging: `git reset HEAD <file>`
2. Add to `.gitignore`
3. Consider using Git LFS for necessary large files

## 📞 Emergency Contacts

If you accidentally push secrets:

1. **Immediately** rotate all exposed credentials
2. Delete the repository if necessary
3. Create a new repository with clean history
4. Review this checklist again

## ✅ Sign-Off

Before pushing, confirm:

- [ ] I have completed ALL items in this checklist
- [ ] I have verified no secrets are committed
- [ ] I have tested the application locally
- [ ] I have reviewed all changes with `git diff`
- [ ] I understand the LICENSE terms
- [ ] I am ready to make this repository public

**Signed:** ________________  
**Date:** ________________

---

**Remember: Once pushed to GitHub, assume it's public forever!**

