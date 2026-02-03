"""Example: call the library layers directly (no CLI)."""

from minitoolchain.contracts import RunConfig, Workflow
from minitoolchain.backends import SimBackend
from minitoolchain.mitigation import ToyMitigator

cfg = RunConfig(backend_name="sim", shots=100, mitigation="toy", circuit="demo", calibration_id="cal-001")
cfg.validate()

wf = Workflow(circuit_spec=cfg.circuit, meta={"note": "example"}, config=cfg)

backend = SimBackend()
raw = backend.execute(wf)
raw.validate_schema()

mitigated = ToyMitigator().apply(raw, cfg)
mitigated.validate_schema()

print("Raw:", raw.to_json())
print("Mitigated:", mitigated.to_json())
