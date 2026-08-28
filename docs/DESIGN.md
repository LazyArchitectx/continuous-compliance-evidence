# Design Notes

Rationale behind the pipeline — written to be defended in a technical interview.

## Why evidence, not just a pass/fail

A boolean "compliant: true" is not auditable. The unit of value here is the **Evidence
artifact**: for each control, the pass/fail *and the measured value that justified it*
(the disparate-impact ratio, the PSI, the PII hit count), timestamped. That is what lets a
risk board accept the result upfront — they can see not just that a control passed, but the
number it passed with, on which run.

## Why controls are data and checks are a registry

The compliance matrix is organizational knowledge that changes without code changes. By
expressing it as `controls.yaml` (control id, the check to run, the threshold) and keeping
checks in a small registry, a new requirement is a YAML row — and only a genuinely new
*kind* of measurement needs a new function. This mirrors how a real governance program
evolves: the matrix churns; the measurement library is stable.

## Why the measured value lives in the artifact

Storing only pass/fail throws away the thing that makes evidence trustworthy and trendable.
Keeping the measured value means the same artifacts can later feed a trend view — you can
watch a control approach its threshold over successive runs and intervene before it fails,
rather than discovering the failure at release time.

## Why a distribution check compares shapes, not pairs

`distribution_shift` uses PSI, which compares the *distribution* of current scores against
the baseline distribution — not row-by-row differences. This is deliberate and worth
understanding: two runs with the same set of scores in a different order have zero drift,
because the population hasn't changed. (This is exactly the kind of subtlety that makes
naive drift checks wrong.)

## Why the CLI can gate a merge

`--fail-on-any` makes the pipeline exit non-zero when any control fails, so it can be wired
as a required CI check: a model change that regresses a control blocks the merge. This is
the bridge from "evidence" to "enforcement" — the same assertions that generate the audit
trail also hold the gate.

## Scope and honesty

The checks are intentionally simple, transparent statistics — the project demonstrates the
*pipeline and evidence discipline*, not novel fairness or drift metrics. A production
version would swap in validated implementations and add the scheduling, signing, and trend
reporting named in the README's "What I'd build next".
