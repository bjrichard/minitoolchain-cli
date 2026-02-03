"""Example: show how warnings appear when calibration_id is missing."""

import warnings
from minitoolchain.contracts import RunConfig, Workflow
from minitoolchain.backends import SimBackend
from minitoolchain.mitigation import ToyMitigator

warnings.simplefilter("always")

cfg = RunConfig(backend_name="sim", shots=50, mitigation="toy", circuit="demo")
cfg.validate()

wf = Workflow(circuit_spec=cfg.circuit, meta={}, config=cfg)

raw = SimBackend().execute(wf)
mitigated = ToyMitigator().apply(raw, cfg)

print(mitigated.to_json())
