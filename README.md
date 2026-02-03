# MiniToolchain (CLI) — Minimal Developer Tools Skeleton

A dependency-light Python skeleton that demonstrates a compiler/tools-style pipeline:

```
CLI/API → RunConfig → Workflow → Backend.execute → Result(raw) → Mitigator.apply → Result(mitigated)
```

This repo is intentionally small and readable. It focuses on:
- explicit validated inputs (fail early)
- stable contracts across layers (schemas/types, not ad hoc dicts)
- traceability via metadata (reproducibility/debuggability)
- a clean post-processing mitigation hook
- tests that lock in contracts

## Quickstart

### 1) Create a virtual environment and install
```bash
python -m venv .venv
source .venv/bin/activate   # mac/linux
# .venv\Scripts\activate  # windows

pip install -e .[dev]
```

### 2) Run the CLI
```bash
minitoolchain run --backend sim --shots 1000 --circuit "demo" --mitigation none

# Mitigation example (toy)
minitoolchain run --backend sim --shots 1000 --circuit "demo" --mitigation toy --calibration-id "cal-001"
```

### 3) Run tests
```bash
pytest -q
```

## What this demonstrates (owner-level invariants)

### Invariant 1 — Explicit, validated inputs at the boundary
- CLI constructs a `RunConfig` and validates required fields (backend, shots, mitigation, circuit).
- Invalid inputs fail fast before any backend execution.
- If mitigation is requested without calibration context, we warn rather than silently proceed.

### Invariant 2 — Stable contracts between layers
- The toolchain uses **structured objects** (`RunConfig`, `Workflow`, `Result`) instead of ad hoc dictionaries.
- `Backend.execute(...)` always returns a `Result` object with a stable schema.
- Mitigation preserves the `Result` schema and records semantic differences via metadata.

### Invariant 3 — Traceability via metadata
- Each `Result` carries required metadata (`run_id`, `backend_name`, `shots`, `mitigation_applied`).
- Additional context (e.g., `calibration_id`, timestamps) is propagated for reproducibility and debugging.

## Design decisions (why it’s structured this way)

- **No external quantum dependencies:** the goal is to highlight tooling/contract design.
- **Backend-specific behavior is isolated:** backend dispatch happens behind a stable interface.
- **Mitigation is post-processing:** the mitigator is a hook that consumes and returns `Result` objects.
- **Contracts are tested:** pytest tests lock in schemas and traceability so refactors stay safe.

## Directory layout

- `src/minitoolchain/cli.py` — CLI entry point (`minitoolchain run ...`)
- `src/minitoolchain/contracts.py` — RunConfig / Workflow / Result data contracts
- `src/minitoolchain/backends.py` — Backend interface + `SimBackend`
- `src/minitoolchain/mitigation.py` — Mitigator interface + `ToyMitigator`
- `examples/` — runnable examples (small scripts)
- `tests/` — pytest contract tests

## Example outputs

Run:
```bash
minitoolchain run --backend sim --shots 10 --circuit "demo" --mitigation none
```

Output (abridged):
```json
{
  "counts": {"0": 5, "1": 5},
  "meta": {
    "backend_name": "sim",
    "mitigation_applied": false,
    "run_id": "...",
    "shots": 10
  }
}
```

## Guiding Principles:

- Fail early at the CLI boundary
- Stable schemas across backends and mitigation
- Metadata traceability for reproducibility
- Small, safe changes protected by tests
