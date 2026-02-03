import pytest

from minitoolchain.contracts import RunConfig, Workflow, Result
from minitoolchain.backends import SimBackend
from minitoolchain.mitigation import ToyMitigator


def test_config_validation_errors():
    with pytest.raises(ValueError):
        RunConfig(backend_name="", shots=10, mitigation="none", circuit="c").validate()
    with pytest.raises(ValueError):
        RunConfig(backend_name="sim", shots=0, mitigation="none", circuit="c").validate()
    with pytest.raises(TypeError):
        RunConfig(backend_name="sim", shots="10", mitigation="none", circuit="c").validate()  # type: ignore


def test_backend_returns_result_schema():
    cfg = RunConfig(backend_name="sim", shots=10, mitigation="none", circuit="c")
    cfg.validate()
    wf = Workflow(circuit_spec="c", meta={}, config=cfg)
    res = SimBackend().execute(wf)
    res.validate_schema()
    assert res.meta["backend_name"] == "sim"
    assert sum(res.counts.values()) == 10


def test_mitigation_preserves_schema_and_sets_metadata():
    cfg = RunConfig(backend_name="sim", shots=100, mitigation="toy", circuit="c", calibration_id="cal-1")
    cfg.validate()
    wf = Workflow(circuit_spec="c", meta={}, config=cfg)
    raw = SimBackend().execute(wf)
    mitigated = ToyMitigator().apply(raw, cfg)
    mitigated.validate_schema()
    assert mitigated.meta["mitigation_applied"] is True
    assert mitigated.meta["mitigation"] == "toy"
    assert sum(mitigated.counts.values()) == cfg.shots


def test_traceability_required_metadata_present():
    cfg = RunConfig(backend_name="sim", shots=10, mitigation="none", circuit="c")
    wf = Workflow(circuit_spec="c", meta={}, config=cfg)
    res = SimBackend().execute(wf)
    # Required keys
    for k in ("run_id", "backend_name", "shots", "mitigation_applied"):
        assert k in res.meta
