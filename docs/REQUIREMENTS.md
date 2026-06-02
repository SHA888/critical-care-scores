# Requirements Specification — Calculable Score Platform

*Reference framework: ISO/IEC/IEEE 29148 (requirements engineering). Software
safety classification per IEC 62304: **Class B** (non-life-supporting; an
incorrect output could contribute to a clinical decision).*

## 1. Purpose & scope

Turn the `critical-care-scores` catalogue into a **live calculator**: anyone can
compute a verified ICU score from a web UI (and, later, mobile), with every cutoff
traceable to a cited source. The catalogue (`SCORES.md`) remains the index; this
layer adds **structured, calculable definitions** and the engines/UI that run them.

## 2. Stakeholders

| Stakeholder | Need |
|---|---|
| Bedside clinician | Fast, correct, offline-capable bedside calculation with provenance |
| Maintainer | Add/verify scores through an auditable, CI-gated pipeline |
| Patient | Inputs never leave the device; results are honest about uncertainty |

## 3. Functional requirements

- **FR-1** Render an input form automatically from a score definition (no per-score UI code).
- **FR-2** Compute the score in-browser and display the numeric result, band, and interpretation.
- **FR-3** Show each score's status, cited references, and a mandatory safety disclaimer.
- **FR-4** Expose **only** scores that pass both the citation contract and the calculation contract.
- **FR-5** Group/browse scores by SCORES.md domain section.
- **FR-6** Validate input types/ranges and report errors without computing a misleading result.

## 4. Non-functional requirements

- **NFR-1 Safety/traceability** — every clinical cutoff cites an `R#` resolvable in `SCORES.md`;
  every definition carries ≥1 golden vector from the primary source.
- **NFR-2 Determinism** — Python and TypeScript engines must produce identical results for all vectors.
- **NFR-3 Privacy** — no patient input is transmitted, stored, or logged (static client-side).
- **NFR-4 Performance** — calculation is synchronous and effectively instant (< 100 ms).
- **NFR-5 Portability** — definitions are language-neutral JSON, reusable by web, mobile, and any API.
- **NFR-6 Accessibility** — labelled inputs, keyboard navigable, sufficient contrast (target WCAG-AA).
- **NFR-7 Cost** — zero-backend hosting (GitHub Pages).

## 5. Constraints

- Python tooling stays **stdlib-only** (`uv run`), matching the existing project.
- The catalogue's citation contract and `unverified` ratchet remain authoritative and unbroken.

## 6. Acceptance criteria (verification hooks)

| Req | Verified by |
|---|---|
| FR-1, FR-2 | `web` renders + `compute()` golden-vector tests (both engines) |
| FR-3, FR-4 | `tools/verify_definitions.py` (status, references, disclaimer, schema) |
| NFR-1 | `verify_definitions.py` reference cross-check vs `SCORES.md` |
| NFR-2 | identical `tests[]` reproduced by `pytest` **and** `vitest` |
| NFR-3 | static SPA; no network calls carry inputs (manual DevTools check) |

## 7. Traceability stub

`requirement → definition field/contract rule → test vector`. Each `scores/<id>.json`
encodes the requirement coverage for one score; its `tests[]` are the acceptance
evidence, executed in CI by both engines and the contract gate.
