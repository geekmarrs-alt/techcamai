---
description: Run the local review gate before pushing (lint, syntax, security).
---

1. Ensure a clean working tree — only intentional changes staged.
2. Install tools on first run if missing:
   ```bash
   pip install yamllint safety==3.2.4 2>/dev/null
   ```
3. Lint GitHub Actions workflows (if any):
   ```bash
   yamllint -d "{extends: relaxed, rules: {line-length: {max: 160}}}" .github/workflows/ 2>/dev/null || true
   ```
4. Check Python syntax across api/ and worker/:
   ```bash
   python3 -m py_compile api/app/main.py api/app/discover.py api/app/shell.py worker/worker.py
   ```
5. Audit Python dependencies for known vulnerabilities:
   ```bash
   for f in $(find . -name "requirements*.txt" 2>/dev/null); do
     safety check --full-report --file "$f"
   done
   ```
6. Summarise results. Fix any failures before committing.
