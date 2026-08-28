"""Runner + evidence tests: the pipeline produces correct verdicts and a blocklist."""

from compliance_evidence.controls import load_controls
from compliance_evidence.runner import run_controls
from compliance_evidence.schema import Control


def _outputs_clean():
    return [
        {"group": "A", "selected": True, "score": 0.5, "baseline_score": 0.5, "text": "ok"},
        {"group": "A", "selected": False, "score": 0.5, "baseline_score": 0.5, "text": "ok"},
        {"group": "B", "selected": True, "score": 0.5, "baseline_score": 0.5, "text": "ok"},
        {"group": "B", "selected": False, "score": 0.5, "baseline_score": 0.5, "text": "ok"},
    ]


def test_clean_run_all_pass_empty_blocklist():
    controls = load_controls("compliance/controls.yaml")
    report = run_controls(controls, _outputs_clean())
    assert report.all_passed is True
    assert report.blocklist == []


def test_failing_run_populates_blocklist():
    controls = load_controls("compliance/controls.yaml")
    bad = [
        {"group": "A", "selected": True, "score": 0.9, "baseline_score": 0.1, "text": "a@b.com"},
        {"group": "A", "selected": True, "score": 0.9, "baseline_score": 0.1, "text": "x"},
        {"group": "B", "selected": False, "score": 0.9, "baseline_score": 0.1, "text": "y"},
        {"group": "B", "selected": False, "score": 0.9, "baseline_score": 0.1, "text": "z"},
    ]
    report = run_controls(controls, bad)
    assert report.all_passed is False
    # disparate impact (skewed), distribution shift (large), and PII (email) all fail
    assert "RMF-MEASURE-2.11" in report.blocklist
    assert "RMF-MEASURE-2.6" in report.blocklist
    assert "RMF-MAP-1.1" in report.blocklist


def test_evidence_carries_measured_value_and_timestamp():
    controls = load_controls("compliance/controls.yaml")
    report = run_controls(controls, _outputs_clean())
    e = report.evidence[0]
    assert e.measured  # not empty — the receipt shows the number it passed with
    assert e.timestamp  # every artifact is timestamped


def test_unknown_assertion_is_reported_as_failure():
    controls = [Control(id="X", name="bogus", assertion="does_not_exist", threshold={})]
    report = run_controls(controls, _outputs_clean())
    assert report.all_passed is False
    assert "unknown assertion" in report.evidence[0].measured["error"]
