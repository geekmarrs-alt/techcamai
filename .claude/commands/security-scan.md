---
description: Run the security scan gate — secrets detection and dependency audit.
---

1. Install tools on first run if missing:
   ```bash
   pip install safety==3.2.4 2>/dev/null
   # gitleaks: https://github.com/gitleaks/gitleaks/releases
   ```
2. Scan for committed secrets:
   ```bash
   gitleaks detect --verbose --redact
   ```
   Resolve any findings before continuing.
3. Audit Python dependencies:
   ```bash
   for f in $(find . -name "requirements*.txt" 2>/dev/null); do
     safety check --full-report --file "$f"
   done
   ```
4. Check .env files are gitignored and not staged:
   ```bash
   git status --short | grep -E "^\?\? .env$|^[AM] .env$" && echo "WARNING: .env may be staged" || echo "OK: .env not staged"
   ```
5. Record findings in commit message Testing section. Clean pass required before push.
