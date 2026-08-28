"""Check-function tests — each metric, pass and fail."""

from compliance_evidence.checks import disparate_impact, distribution_shift, pii_scan


def test_disparate_impact_balanced_passes():
    outputs = [
        {"group": "A", "selected": True},
        {"group": "A", "selected": False},
        {"group": "B", "selected": True},
        {"group": "B", "selected": False},
    ]
    passed, measured = disparate_impact(outputs, {"min_ratio": 0.8})
    assert passed is True
    assert measured["ratio"] == 1.0


def test_disparate_impact_skewed_fails():
    outputs = [
        {"group": "A", "selected": True},
        {"group": "A", "selected": True},
        {"group": "B", "selected": False},
        {"group": "B", "selected": False},
    ]
    passed, measured = disparate_impact(outputs, {"min_ratio": 0.8})
    assert passed is False
    assert measured["ratio"] < 0.8


def test_distribution_shift_stable_passes():
    outputs = [{"score": 0.5, "baseline_score": 0.5} for _ in range(20)]
    passed, measured = distribution_shift(outputs, {"max_psi": 0.2})
    assert passed is True
    assert measured["psi"] <= 0.2


def test_distribution_shift_large_fails():
    outputs = [{"score": 0.9, "baseline_score": 0.1} for _ in range(20)]
    passed, measured = distribution_shift(outputs, {"max_psi": 0.2})
    assert passed is False
    assert measured["psi"] > 0.2


def test_pii_scan_clean_passes():
    outputs = [{"text": "nothing sensitive here"}]
    passed, measured = pii_scan(outputs, {"max_hits": 0})
    assert passed is True
    assert measured["hits"] == 0


def test_pii_scan_catches_email_ssn_secret():
    outputs = [
        {"text": "reach me at a@b.com"},
        {"text": "SSN 123-45-6789"},
        {"text": "sk-live-abcdef123456"},
    ]
    passed, measured = pii_scan(outputs, {"max_hits": 0})
    assert passed is False
    assert measured["hits"] == 3
