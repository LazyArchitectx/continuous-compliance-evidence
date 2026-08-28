"""CLI tests: it runs, writes evidence, and gates via exit code."""

import json

from compliance_evidence.cli import main


def test_cli_clean_passes(capsys):
    rc = main(["--controls", "compliance/controls.yaml", "--outputs", "data/outputs_clean.jsonl"])
    out = capsys.readouterr().out.strip().splitlines()
    summary = json.loads(out[-1])["summary"]
    assert rc == 0
    assert summary["all_passed"] is True
    assert summary["blocklist"] == []


def test_cli_failing_gate_returns_nonzero(capsys):
    rc = main(
        [
            "--controls", "compliance/controls.yaml",
            "--outputs", "data/outputs_failing.jsonl",
            "--fail-on-any",
        ]
    )
    summary = json.loads(capsys.readouterr().out.strip().splitlines()[-1])["summary"]
    assert rc == 1  # gate blocks
    assert summary["all_passed"] is False
    assert summary["blocklist"]


def test_cli_writes_evidence_artifacts(tmp_path, capsys):
    ev = tmp_path / "evidence"
    rc = main(
        [
            "--controls", "compliance/controls.yaml",
            "--outputs", "data/outputs_clean.jsonl",
            "--evidence-dir", str(ev),
        ]
    )
    assert rc == 0
    # one dated folder with one json per control
    dated = list(ev.iterdir())
    assert len(dated) == 1
    artifacts = list(dated[0].glob("*.json"))
    assert len(artifacts) == 3
    sample = json.loads(artifacts[0].read_text())
    assert "timestamp" in sample and "measured" in sample
