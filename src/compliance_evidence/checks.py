"""Assertion checks. Each maps a compliance control to a runnable measurement.

Each check takes the model outputs plus the control's threshold and returns
(passed, measured) — a boolean and the measured value(s) that justify it. The
measured value is what makes the evidence auditable: not just "passed", but the
number it passed with.

These are deliberately simple, transparent statistics — the point of the project
is the pipeline and evidence discipline, not novel metrics.
"""

from __future__ import annotations

import math
import re
from typing import Any

Outputs = list[dict[str, Any]]


def disparate_impact(outputs: Outputs, threshold: dict) -> tuple[bool, dict]:
    """Ratio of selection rates between groups (the '80% rule' style check).

    Each output carries {'group': str, 'selected': bool}. Passes if the ratio
    (min rate / max rate) is >= threshold['min_ratio'] (default 0.8).
    """
    groups: dict[str, list[bool]] = {}
    for o in outputs:
        groups.setdefault(o.get("group", "unknown"), []).append(bool(o.get("selected")))
    rates = {g: sum(v) / len(v) for g, v in groups.items() if v}
    if len(rates) < 2:
        return True, {"ratio": 1.0, "note": "fewer than two groups"}
    lo, hi = min(rates.values()), max(rates.values())
    ratio = (lo / hi) if hi > 0 else 1.0
    return ratio >= threshold.get("min_ratio", 0.8), {
        "ratio": round(ratio, 4),
        "rates": {g: round(r, 4) for g, r in rates.items()},
    }


def distribution_shift(outputs: Outputs, threshold: dict) -> tuple[bool, dict]:
    """Population Stability Index between baseline and current score distributions.

    Each output carries {'score': float, 'baseline_score': float}. Passes if PSI
    is <= threshold['max_psi'] (default 0.2).
    """
    cur = [float(o["score"]) for o in outputs if "score" in o]
    base = [float(o["baseline_score"]) for o in outputs if "baseline_score" in o]
    if not cur or not base:
        return True, {"psi": 0.0, "note": "insufficient data"}
    psi = _psi(base, cur)
    return psi <= threshold.get("max_psi", 0.2), {"psi": round(psi, 4)}


def pii_scan(outputs: Outputs, threshold: dict) -> tuple[bool, dict]:
    """Count outputs containing PII-like patterns. Passes if hits <= max_hits (default 0)."""
    patterns = [
        r"[\w.+-]+@[\w-]+\.[\w.-]+",   # email
        r"\b\d{3}-\d{2}-\d{4}\b",       # SSN-shaped
        r"sk-[A-Za-z0-9\-]{6,}",        # api secret
    ]
    hits = sum(
        1 for o in outputs if any(re.search(p, str(o.get("text", ""))) for p in patterns)
    )
    return hits <= threshold.get("max_hits", 0), {"hits": hits}


def _psi(expected: list[float], actual: list[float], bins: int = 10) -> float:
    lo, hi = min(expected + actual), max(expected + actual)
    if hi == lo:
        return 0.0
    width = (hi - lo) / bins

    def dist(xs: list[float]) -> list[float]:
        counts = [0] * bins
        for x in xs:
            idx = min(int((x - lo) / width), bins - 1)
            counts[idx] += 1
        n = len(xs) or 1
        return [c / n for c in counts]

    e, a = dist(expected), dist(actual)
    psi = 0.0
    for ei, ai in zip(e, a):
        ei = ei or 1e-6
        ai = ai or 1e-6
        psi += (ai - ei) * math.log(ai / ei)
    return abs(psi)


REGISTRY = {
    "disparate_impact": disparate_impact,
    "distribution_shift": distribution_shift,
    "pii_scan": pii_scan,
}
