# Risk Management

*Reference framework: ISO 14971 (medical-device risk management). This is a
pragmatic hazard analysis for a Class-B clinical-decision-support calculator, not
a formal regulatory file.*

## Hazard analysis

| ID | Hazard (what could harm) | Cause | Risk control(s) | Residual |
|----|--------------------------|-------|-----------------|----------|
| H1 | Calculator returns a wrong score → wrong clinical decision | Mis-transcribed cutoff/formula | Every cutoff cites an `R#`; golden vectors from the primary source; **dual-engine** agreement gate in CI | Low |
| H2 | Web and (future) mobile compute different results | Divergent reimplementation | Single shared `scores/*.json` + golden vectors both engines must pass; rounding pinned half-up in both | Low |
| H3 | Rounding/precision drift | Banker's vs half-up rounding across languages | `round` = `floor(x+0.5)` in both engines; covered by vectors | Low |
| H4 | User trusts an unverified score | Exposing a score lacking a checked source | Calculator exposes **only** scores passing both contracts; `unverified` rows stay reference-only | Low |
| H5 | Patient data leakage | Server-side processing / telemetry | Static client-side; **no input transmitted, stored, or logged**; no analytics on inputs | Low |
| H6 | Stale guideline presented as current | Definition not re-verified after a guideline change | `status` + references + encode-date shown in UI; re-verification triggers in `TODO.md` also re-check formulas | Medium |
| H7 | Over-reliance / use outside intended context | Score applied to wrong population/condition | Persistent global disclaimer + per-score disclaimer + "verify against primary source" note | Medium |
| H8 | Unsafe expression evaluation | Arbitrary code in a formula string | No `eval`/`Function`; whitelisted AST/grammar; schema constrains `expr` | Low |
| H9 | Invalid input produces a misleading number | Out-of-range / wrong-type entry | Engine validates type, range, enum membership; UI blocks compute until inputs valid | Low |

## Risk-control verification

- H1–H3, H8, H9 — automated: `pytest` (Python), `vitest` (TS), `verify_definitions.py` (gate). CI-blocking.
- H4 — gate rule: status ∈ {current, superseded, contested} and references resolve.
- H5 — design control; manual DevTools check that no request carries input values.
- H6 — process control: maintenance loop + `TODO.md` re-verification triggers.
- H7 — labelling control: disclaimers present and surfaced in the UI.

## Post-market / maintenance

A "report a wrong cutoff" issue path feeds H1/H6. Any change to a definition re-runs
both engines and the gate before merge; releases are semantically versioned.
