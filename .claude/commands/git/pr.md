---
description: Create a pull request from the current branch.
argument-hint: [target-branch]
---

## Variables

TARGET_BRANCH: $1 (defaults to `main`)
SOURCE_BRANCH: current branch (`git branch --show-current`)

## Workflow

1. Ensure `/review` and `/security-scan` have passed locally.
2. Create the PR using GitHub MCP tools (mcp__github__create_pull_request):
   - base: TARGET_BRANCH
   - head: SOURCE_BRANCH
   - title: Conventional PR title
   - body: Summary referencing Context, Testing, and Security results.
3. Share the PR link with reviewers and ensure at least one human approval is obtained.
