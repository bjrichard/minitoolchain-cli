from __future__ import annotations

import argparse
import warnings
from typing import Dict, Any

from .contracts import RunConfig, Workflow
from .backends import SimBackend
from .mitigation import ToyMitigator


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="minitoolchain", description="Minimal toolchain CLI demo")
    sub = p.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="Run a workflow")
    run.add_argument("--backend", required=True, help="Backend name (e.g., sim)")
    run.add_argument("--shots", type=int, default=1000, help="Number of shots (positive int)")
    run.add_argument("--circuit", required=True, help="Circuit spec placeholder (string)")
    run.add_argument("--mitigation", default="none", help="Mitigation name (none|toy)")
    run.add_argument("--calibration-id", default=None, help="Calibration context identifier (optional)")
    return p


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "run":
        raise ValueError("Unsupported command")

    cfg = RunConfig(
        backend_name=args.backend,
        shots=args.shots,
        mitigation=args.mitigation,
        circuit=args.circuit,
        calibration_id=args.calibration_id,
    )
    cfg.validate()

    if cfg.mitigation != "none" and cfg.calibration_id is None:
        warnings.warn("Mitigation enabled without calibration_id. Consider providing --calibration-id.", RuntimeWarning)

    # Build a backend-agnostic workflow.
    workflow = Workflow(
        circuit_spec=cfg.circuit,
        meta={"note": "placeholder workflow meta"},
        config=cfg,
    )

    # Backend dispatch (minimal).
    if cfg.backend_name == "sim":
        backend = SimBackend()
    else:
        raise ValueError(f"Unsupported backend '{cfg.backend_name}'. Try --backend sim")

    result = backend.execute(workflow)
    result.validate_schema()

    # Mitigation hook.
    if cfg.mitigation == "toy":
        mitigator = ToyMitigator()
        result = mitigator.apply(result, cfg)
        result.validate_schema()
    elif cfg.mitigation != "none":
        raise ValueError(f"Unsupported mitigation '{cfg.mitigation}'. Try --mitigation none|toy")

    print(result.to_json())
