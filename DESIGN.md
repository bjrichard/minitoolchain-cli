# Design Notes

This repository is intentionally minimal. It demonstrates engineering behaviors that matter in developer-tools roles:

- **Fail early at boundaries**: validate user inputs before expensive operations.
- **Stable contracts**: structured objects define schemas at each layer.
- **Traceability**: results include metadata required for reproducibility and debugging.
- **Mitigation as post-processing**: semantic changes are reflected in metadata, not schema drift.
- **Tests as guardrails**: contract tests prevent regressions when refactoring.

## Pipeline

CLI/API → RunConfig → Workflow → Backend.execute → Result(raw) → Mitigator.apply → Result(mitigated)

## Extension ideas (not implemented)

- Add additional backends with capability discovery.
- Add result uncertainty fields and richer calibration context.
- Add a registry mechanism for backends and mitigators.
