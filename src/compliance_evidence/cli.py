"""Command-line interface for the compliance evidence pipeline.

Examples
--------
    compliance-run --controls compliance/controls.yaml --outputs data/outputs.jsonl
    compliance-run --controls compliance/controls.yaml --outputs data/outputs.jsonl \\
                   --evidence-dir evidence --fail-on-any
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from compliance_evidence.controls import load_controls
from compliance_evidence.runner import run_controls


def _load_outputs(path: str) -> list[dict]:
    lines = Path(path).read_text().splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def _run(args: argparse.Namespace) -> int:
    controls = load_controls(args.controls)
    outputs = _load_outputs(args.outputs)
    report = run_controls(controls, outputs)

    # Emit one immutable evidence artifact per control, under a dated folder.
    if args.evidence_dir:
        out_dir = Path(args.evidence_dir) / datetime.now(timezone.utc).date().isoformat()
        out_dir.mkdir(parents=True, exist_ok=True)
        for e in report.evidence:
            (out_dir / f"{e.control_id}.json").write_text(e.model_dump_json(indent=2))

    for e in report.evidence:
        print(
            json.dumps(
                {
                    "control": e.control_id,
                    "name": e.control_name,
                    "passed": e.passed,
                    "measured": e.measured,
                }
            )
        )
    print(json.dumps({"summary": {"all_passed": report.all_passed, "blocklist": report.blocklist}}))

    if args.fail_on_any and not report.all_passed:
        return 1  # non-zero so a CI gate blocks the merge
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="compliance-run", description=__doc__)
    parser.add_argument("--controls", default="compliance/controls.yaml")
    parser.add_argument("--outputs", required=True, help="JSONL of model outputs to check")
    parser.add_argument("--evidence-dir", default=None, help="write evidence artifacts here")
    parser.add_argument(
        "--fail-on-any", action="store_true", help="exit non-zero if any control fails"
    )
    args = parser.parse_args(argv)
    if not Path(args.controls).exists():
        print(f"controls file not found: {args.controls}", file=sys.stderr)
        return 2
    return _run(args)


if __name__ == "__main__":
    raise SystemExit(main())
