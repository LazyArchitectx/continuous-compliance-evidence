"""Run every control against a set of outputs and emit evidence.

This is the nightly job's core: for each control, look up its check in the
registry, run it, and produce an immutable Evidence artifact. Any failure lands
the control on the blocklist. The RunReport is the risk board's review package —
pre-generated, so the sign-off already exists by the time anyone asks.
"""

from __future__ import annotations

from typing import Any

from compliance_evidence.checks import REGISTRY
from compliance_evidence.schema import Control, Evidence, RunReport


def run_controls(controls: list[Control], outputs: list[dict[str, Any]]) -> RunReport:
    evidence: list[Evidence] = []
    for control in controls:
        check = REGISTRY.get(control.assertion)
        if check is None:
            evidence.append(
                Evidence(
                    control_id=control.id,
                    control_name=control.name,
                    passed=False,
                    measured={"error": f"unknown assertion '{control.assertion}'"},
                    threshold=control.threshold,
                )
            )
            continue
        passed, measured = check(outputs, control.threshold)
        evidence.append(
            Evidence(
                control_id=control.id,
                control_name=control.name,
                passed=passed,
                measured=measured,
                threshold=control.threshold,
            )
        )
    return RunReport(evidence=evidence)
