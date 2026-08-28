"""Load the compliance matrix (controls) from YAML."""

from __future__ import annotations

from pathlib import Path

import yaml

from compliance_evidence.schema import Control


def load_controls(path: str | Path) -> list[Control]:
    """Load and validate the controls registry — the transcribed compliance matrix."""
    raw = yaml.safe_load(Path(path).read_text())
    return [Control.model_validate(c) for c in raw["controls"]]
