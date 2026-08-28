# Continuous Compliance Evidence Pipeline

Turns a static compliance matrix into **continuously generated, auto-produced
evidence**. Each governance control (a risk-board requirement) becomes a runnable
check; a single run executes them all against a model's outputs, emits an immutable
**evidence artifact** per control, and flags any failure to a **blocklist**. The point:
a governance sign-off that took weeks becomes a build artifact that already exists by
the time anyone asks for it.

[![ci](https://github.com/LazyArchitectx/continuous-compliance-evidence/actions/workflows/ci.yml/badge.svg)](https://github.com/LazyArchitectx/continuous-compliance-evidence/actions)

> **What this is.** A portfolio demonstrator of the *compliance-as-continuous-evidence*
> pattern — mapping NIST-AI-RMF-style controls to automated checks that produce an audit
> trail on every run. A clean, from-scratch implementation, not a proprietary system, and
> it ships no confidential data.

---

## The idea

Manual compliance review is a bottleneck: every model release waits on document sign-offs.
This pipeline makes the review **executable**. The risk board's static matrix is
transcribed row-by-row into `controls.yaml` — each row names a control, the check that
proves it, and its threshold. A run produces, per control, a structured receipt: pass/fail
**plus the measured value it passed with**, timestamped. The evidence is the review
package, pre-generated.

## Architecture

```
   controls.yaml ─► Runner ─► for each control:
   (the matrix)                run its check against the outputs
                               │
                               ▼
                         Evidence artifact  {control, measured, pass/fail, ts}
                               │
                               ├─ fail ─► blocklist
                               ▼
                         RunReport  (all_passed, blocklist)  ─► optional CI gate
```

Controls are **data**, checks are a small **registry** (`disparate_impact`,
`distribution_shift`, `pii_scan`). Adding a control means adding a YAML row and, if new,
one check function — the engine stays untouched.

## Quickstart

```bash
pip install -e ".[dev]"

# Clean outputs -> everything passes, empty blocklist:
compliance-run --controls compliance/controls.yaml --outputs data/outputs_clean.jsonl

# Failing outputs -> controls land on the blocklist:
compliance-run --controls compliance/controls.yaml --outputs data/outputs_failing.jsonl
```

Write immutable evidence artifacts and act as a **CI gate** (non-zero exit blocks a merge):

```bash
compliance-run --controls compliance/controls.yaml --outputs data/outputs_failing.jsonl \
               --evidence-dir evidence --fail-on-any
```

The failing run's summary:

```json
{"summary": {"all_passed": false,
             "blocklist": ["RMF-MEASURE-2.11", "RMF-MEASURE-2.6", "RMF-MAP-1.1"]}}
```

## Testing

```bash
ruff check .     # lint
pytest -v        # 13 tests
```

`tests/test_runner.py` proves the blocklist populates correctly; `tests/test_cli.py`
proves the `--fail-on-any` gate returns a non-zero exit and that evidence artifacts are
written with their measured values and timestamps.

## Project layout

```
compliance/controls.yaml      the matrix: control -> check -> threshold
src/compliance_evidence/
  schema.py                   Control, Evidence, RunReport (Pydantic)
  checks.py                   disparate_impact, distribution_shift, pii_scan
  controls.py                 load the matrix
  runner.py                   run all controls -> evidence + blocklist
  cli.py                      compliance-run ...
tests/                        checks, runner, CLI
docs/DESIGN.md                deeper architecture + rationale
```

## What I'd build next

- A scheduled workflow (nightly) that runs the pipeline and commits the evidence folder.
- A trend view: measured values per control over time, to see drift before it fails.
- Signed evidence artifacts, so the audit trail is tamper-evident.

## License

MIT — see [LICENSE](LICENSE).
