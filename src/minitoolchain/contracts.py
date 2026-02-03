from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import json
import uuid


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class RunConfig:
    """User-controlled parameters at the CLI/API boundary."""

    backend_name: str
    shots: int
    mitigation: str  # e.g. "none" or mitigator name
    circuit: str

    # Traceability
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=_utc_now_iso)

    # Optional context
    calibration_id: Optional[str] = None
    tags: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if not isinstance(self.backend_name, str) or self.backend_name.strip() == "":
            raise ValueError("backend_name must be a non-empty string")

        if not isinstance(self.shots, int):
            raise TypeError(f"shots must be an int, got {type(self.shots).__name__}")
        if self.shots <= 0:
            raise ValueError("shots must be a positive integer")

        if not isinstance(self.mitigation, str) or self.mitigation.strip() == "":
            raise ValueError("mitigation must be a non-empty string (e.g., 'none' or a mitigator name)")

        if not isinstance(self.circuit, str) or self.circuit.strip() == "":
            raise ValueError("circuit must be a non-empty string")


@dataclass(frozen=True)
class Workflow:
    """Backend-agnostic job description derived from user intent."""

    circuit_spec: Any  # placeholder (string/dict/etc.)
    meta: Dict[str, Any]
    config: RunConfig


@dataclass(frozen=True)
class Result:
    """Stable output schema across backends and mitigation steps."""

    counts: Dict[str, int]
    meta: Dict[str, Any]
    raw: Dict[str, Any] = field(default_factory=dict)

    def validate_schema(self) -> None:
        if "run_id" not in self.meta:
            raise KeyError("Result.meta missing required key: 'run_id'")
        if "backend_name" not in self.meta:
            raise KeyError("Result.meta missing required key: 'backend_name'")
        if "shots" not in self.meta:
            raise KeyError("Result.meta missing required key: 'shots'")
        if "mitigation_applied" not in self.meta:
            raise KeyError("Result.meta missing required key: 'mitigation_applied'")

        if not isinstance(self.counts, dict) or len(self.counts) == 0:
            raise ValueError("Result.counts must be a non-empty dict")

        # basic integrity: counts should be ints >= 0
        for k, v in self.counts.items():
            if not isinstance(k, str):
                raise TypeError("Result.counts keys must be str")
            if not isinstance(v, int):
                raise TypeError("Result.counts values must be int")
            if v < 0:
                raise ValueError("Result.counts values must be >= 0")

    def to_json(self) -> str:
        return json.dumps({"counts": self.counts, "meta": self.meta, "raw": self.raw}, indent=2, sort_keys=True)
