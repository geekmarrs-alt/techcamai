# Repository organization guide

This project is structured as one application in one repository.

## Application layout

- `api/` - backend service and operator dashboard UI
- `worker/` - camera polling and detection loop
- `windows/` - Windows installer and launch helpers
- `docs/` - setup, architecture, and operations documentation
- `tests/` - repository-level tests
- `web/` - future marketing site placeholder (not part of runtime stack)

## Branch strategy

Use a simple branch model:

1. `master` is always deployable.
2. Create small feature branches from `master`.
3. Merge to `master` quickly.
4. Delete merged branches.

### Cleanup

Use the GitHub branches page to delete merged branches after the consolidation branch lands.

## Keeping one active line of work

If you want only one branch to work from:

1. Use `master` directly for operational updates, or
2. Keep one long-lived branch (for example `production`) and merge everything into it.

For most teams, option #1 (`master` as source-of-truth) is simplest.
