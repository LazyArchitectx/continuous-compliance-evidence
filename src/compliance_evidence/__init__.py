"""Continuous compliance evidence pipeline.

Turns a static compliance matrix (control -> assertion -> threshold) into
continuously generated, auto-produced evidence. Each control maps to a runnable
check; a nightly run executes them all against a model's outputs, emits a
structured evidence artifact per control, and flags any failure to a blocklist.
The point: a governance sign-off that took weeks becomes a build artifact that
already exists by the time anyone asks for it.
"""

from compliance_evidence.controls import load_controls
from compliance_evidence.runner import run_controls
from compliance_evidence.schema import Control, Evidence, RunReport

__all__ = ["Control", "Evidence", "RunReport", "load_controls", "run_controls"]
__version__ = "1.0.0"
