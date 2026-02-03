from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol
from datetime import datetime, timezone

from .contracts import Workflow, Result


@dataclass(frozen=True)
class BackendCapabilities:
    name: str
    max_qubits: int
    supported_ops: set[str]
    notes: str | None = None


class Backend(Protocol):
    def capabilities(self) -> BackendCapabilities: ...
    def execute(self, workflow: Workflow) -> Result: ...


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class SimBackend:
    """A minimal backend that returns deterministic-ish counts for demo purposes."""

    def __init__(self) -> None:
        self._caps = BackendCapabilities(name="sim", max_qubits=32, supported_ops={"measure", "x", "h", "cx"})

    def capabilities(self) -> BackendCapabilities:
        return self._caps

    def execute(self, workflow: Workflow) -> Result:
        cfg = workflow.config
        shots = cfg.shots

        # Fake counts: split shots between two outcomes for repeatability.
        counts = {"0": shots // 2, "1": shots - shots // 2}

        meta: Dict[str, Any] = {
            "run_id": cfg.run_id,
            "backend_name": cfg.backend_name,
            "shots": shots,
            "mitigation_applied": False,
            "created_at": cfg.created_at,
            "executed_at": _utc_now_iso(),
            "calibration_id": cfg.calibration_id,
            "circuit": cfg.circuit,
        }

        raw: Dict[str, Any] = {"note": "simulated backend raw payload placeholder"}
        return Result(counts=counts, meta=meta, raw=raw)
