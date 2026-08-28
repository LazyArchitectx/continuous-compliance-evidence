"""Validated data models for controls, evidence artifacts, and the run report."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class Control(BaseModel):
    """One row of the compliance matrix, made executable.

    `assertion` names the check function (e.g. 'disparate_impact'); `threshold`
    carries its parameters. This is the transcription of a risk board's static
    matrix into something a machine can run and prove.
    """

    id: str
    name: str
    assertion: str
    threshold: dict[str, Any] = Field(default_factory=dict)


class Evidence(BaseModel):
    """The receipt produced for one control on one run.

    Immutable by convention: written once per run, never edited — so the trail is
    a build artifact, not a document someone can revise after the fact.
    """

    control_id: str
    control_name: str
    passed: bool
    measured: dict[str, Any]
    threshold: dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def blocklisted(self) -> bool:
        return not self.passed


class RunReport(BaseModel):
    """The result of running every control once."""

    evidence: list[Evidence]

    @property
    def all_passed(self) -> bool:
        return all(e.passed for e in self.evidence)

    @property
    def blocklist(self) -> list[str]:
        return [e.control_id for e in self.evidence if e.blocklisted]
