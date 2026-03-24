---
description: Create a pull request from the current branch.
argument-hint: [target-branch]
---

## Variables

TARGET_BRANCH: $1 (defaults to `master`)
SOURCE_BRANCH: current branch (`git branch --show-current`)

## Workflow

1. Ensure `/review` and `/security-scan` have passed locally.
2. Confirm CI workflows succeeded for `SOURCE_BRANCH`.
3. Create the PR using GitHub CLI:
   ```bash
   gh pr create \
     --base "$TARGET_BRANCH" \
     --head "$SOURCE_BRANCH" \
     --title "<Conventional PR title>" \
     --body "## Summary\n\n## Test plan\n\n## Security notes"
   ```
4. Share the PR link with reviewers and ensure at least one human approval is obtained.
