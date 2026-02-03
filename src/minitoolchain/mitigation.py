from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Protocol, Any, Dict

from .contracts import Result, RunConfig


class Mitigator(Protocol):
    name: str
    def apply(self, result: Result, config: RunConfig) -> Result: ...


@dataclass(frozen=True)
class ToyMitigator:
    """A toy mitigator that 'rebalances' counts slightly.

    This is NOT physically meaningful mitigation; it exists to demonstrate:
    - post-processing hook
    - stable schema preservation
    - metadata traceability
    """

    name: str = "toy"

    def apply(self, result: Result, config: RunConfig) -> Result:
        # Warn if mitigation requested but calibration context missing.
        if config.calibration_id is None:
            warnings.warn(
                "Mitigation requested but calibration_id is missing. Proceeding anyway; results may be unreliable.",
                RuntimeWarning,
            )

        counts = dict(result.counts)

        # Simple, bounded adjustment: move 1% of shots from the max bucket to the min bucket.
        total = sum(counts.values())
        if total <= 0:
            raise ValueError("Cannot mitigate empty counts")

        keys = list(counts.keys())
        max_k = max(keys, key=lambda k: counts[k])
        min_k = min(keys, key=lambda k: counts[k])

        delta = max(1, total // 100)  # 1% or at least 1
        delta = min(delta, counts[max_k])  # don't go negative

        counts[max_k] -= delta
        counts[min_k] += delta

        meta: Dict[str, Any] = dict(result.meta)
        meta["mitigation_applied"] = True
        meta["mitigation"] = self.name
        meta["mitigation_assumptions"] = {
            "note": "toy mitigator; demonstrates post-processing contracts only",
            "calibration_id_used": config.calibration_id,
        }

        return Result(counts=counts, meta=meta, raw=dict(result.raw))
