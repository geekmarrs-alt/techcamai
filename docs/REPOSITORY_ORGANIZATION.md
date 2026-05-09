# Repository organization guide

This project is structured as one application in one repository.

## Application layout

- `api/` - backend service and operator dashboard UI
- `worker/` - camera polling and detection loop
- `pi/` - Raspberry Pi packaging and deployment scripts
- `docs/` - setup, architecture, and operations documentation
- `tests/` - repository-level tests
- `web/` - future marketing site placeholder (not part of runtime stack)

## Branch strategy

Use a simple branch model:

1. `master` is always deployable.
2. Create small feature branches from `master`.
3. Merge to `master` quickly.
4. Delete merged branches.

### Local cleanup

```bash
git checkout master
git pull origin master
git fetch --prune
git branch --merged | rg -v "^\*|master$" | xargs -r git branch -d
```

### Remote cleanup (GitHub)

Use the GitHub "Branches" page to delete merged branches, or run:

```bash
git push origin --delete <branch-name>
```

## Keeping one active line of work

If you want only one branch to work from:

1. Use `master` directly for operational updates, or
2. Keep one long-lived branch (for example `production`) and merge everything into it.

For most teams, option #1 (`master` as source-of-truth) is simplest.
